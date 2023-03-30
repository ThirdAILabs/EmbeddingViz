export MODEL_PATH="/share/embeddings/data/stackoverflow/bigticketsearch.bolt"
export CATALOG_PATH="/share/embeddings/data/stackoverflow/qna-100000-compact-nonewlines-noescapes-cleanids.csv"
export API_PREFIX="/stackoverflow"

python3 generate_graph.py \
--catalog_path /share/embeddings/data/stackoverflow/qna-100000-all.csv \
--strong_column_names title question_body  \
--target_name "id" \
--neighbours 20 \
--threshold 20 \
--output-dir /share/embeddings/copy_EmbeddingViz/EmbeddingViz/data \
--embed-path /share/embeddings/data/stackoverflow/defaultembeddings.npy