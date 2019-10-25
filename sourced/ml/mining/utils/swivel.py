import logging
from pathlib import Path
import shutil
from typing import List, Optional
import warnings

import numpy as np
from scipy.sparse import csr_matrix
import tqdm

try:
    import tensorflow as tf
except ImportError:
    warnings.warn(
        "Tensorflow is not installed, dependent functionality is unavailable."
    )

VOCABULARY_FILENAME = "%s_vocab.txt"
SUMS_FILENAME = "%s_sums.txt"
SHARDS_FILENAME = "shard-%03d-%03d.pb"


def format_int_list(vs: List[int]):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=list(vs)))


def format_float_list(vs: List[float]):
    return tf.train.Feature(float_list=tf.train.FloatList(value=list(vs)))


def create_vocabulary_sums_inputs(
    output_dir: Path,
    label: str,
    log: logging.Logger,
    indptr: np.ndarray,
    shard_size: int,
    vocab: List,
) -> np.ndarray:
    """Create and save the Swivel inputs for either the column or row vocabulary, then return the
    new order to be used when creating the matrix."""
    vocab_size = len(vocab)
    if vocab_size < shard_size:
        log.error(
            "Vocabulary size (%d) is less than shard size (%d), please specify a smaller shard "
            "size, aborting",
            vocab_size,
            shard_size,
        )
        raise RuntimeError
    log.info("Reordering the vocabulary in descending order of feature frequency ...")
    bool_sums = indptr[1:] - indptr[:-1]
    reorder = np.argsort(-bool_sums)
    vocab_size -= vocab_size % shard_size
    num_removed = len(reorder) - vocab_size
    log.info("Effective vocabulary size: %d", vocab_size)
    if num_removed:
        log.info(
            "Removing the %d least important %ss of the vocabulary", num_removed, label
        )
        vocab = np.delete(vocab, reorder[vocab_size:]).tolist()
        bool_sums = np.delete(bool_sums, reorder[vocab_size:])
        reorder = reorder[:vocab_size]
    vocab_output_path = output_dir / (VOCABULARY_FILENAME % label)
    log.info("Saving the vocabulary to %s ...", vocab_output_path)
    with vocab_output_path.open() as fout:
        fout.write("\n".join(vocab))
    sums_output_path = output_dir / (SUMS_FILENAME % label)
    log.info("Saving the sums to %s ...", sums_output_path)
    with sums_output_path.open() as fout:
        fout.write("\n".join(map(str, bool_sums.tolist())))
    return reorder


def create_swivel_inputs(
    output_dir: Path,
    log: logging.Logger,
    coocs_matrix: csr_matrix,
    shard_size: int,
    row_vocab: List,
    col_vocab: Optional[List] = None,
):
    """Create and save Swivel inputs from a given co-occurence matrix. If column vocabulary is not
    given, the matrix must be square (and should be symmetrical)."""

    if coocs_matrix.shape[0] != len(row_vocab):
        log.error("Row vocabulary and matrix shape do not match, aborting")
        raise RuntimeError

    if col_vocab and coocs_matrix.shape[1] != len(col_vocab):
        log.error("Column vocabulary and matrix shape do not match, aborting")
        raise RuntimeError
    elif not col_vocab and coocs_matrix.shape[0] != coocs_matrix.shape[1]:
        log.error(
            "Co-occurence matrix is not square but no column vocabulary was provided, aborting"
        )
        raise RuntimeError
    log.info("Creating and saving the rows vocabulary and sums ... ")
    row_reorder = create_vocabulary_sums_inputs(
        output_dir, "row", log, coocs_matrix.indptr, shard_size, row_vocab
    )
    row_nshards = len(row_reorder) // shard_size
    if col_vocab:
        log.info("Creating and saving the columns vocabulary and sums ... ")
        col_reorder = create_vocabulary_sums_inputs(
            output_dir, "col", log, coocs_matrix.tocsc().indptr, shard_size, col_vocab
        )
        col_nshards = len(col_reorder) // shard_size
    else:
        col_reorder = row_reorder
        col_nshards = row_nshards
        for filename in [VOCABULARY_FILENAME, SUMS_FILENAME]:
            row_filepath = (output_dir / (filename % "row")).as_posix()
            col_filepath = (output_dir / (filename % "col")).as_posix()
            log.info("Copying %s to %s ...", row_filepath, col_filepath)
            shutil.copyfile(row_filepath, col_filepath)
    n_shards = row_nshards * col_nshards
    log.info("Creating and saving the %d shards ...", n_shards)
    with tqdm(total=n_shards) as progress:
        for row in range(row_nshards):
            indices_row = row_reorder[row::row_nshards]
            for col in range(col_nshards):
                indices_col = col_reorder[col::col_nshards]
                shard = coocs_matrix[indices_row][:, indices_col].tocoo()
                tf_shard = tf.train.Example(
                    features=tf.train.Features(
                        feature={
                            "global_row": format_int_list(indices_row),
                            "global_col": format_int_list(indices_col),
                            "sparse_local_row": format_int_list(shard.row),
                            "sparse_local_col": format_int_list(shard.col),
                            "sparse_value": format_float_list(shard.data),
                        }
                    )
                )
                with (output_dir / (SHARDS_FILENAME % (row, col))).open(
                    mode="rb"
                ) as fout:
                    fout.write(tf_shard.SerializeToString())

                progress.update(1)
