# Use conda python environment
Sys.setenv(RETICULATE_PYTHON="/home/joe/anaconda3/envs/R_python/bin/python")

# Load libraries
library(rhdf5)
library(CytoTRACE)

# Read in exported scVI data - rows are genes columns are cells
data <- h5read(
    "/mnt/iacchus/joe/processed_data/M_cell/thymus_scVI_expression_CYTOtrace.hdf5", # nolint: line_length_linter.
    "data"
)

data_matrix <- data.frame(data$block0_values, row.names = data$axis0)
colnames(data_matrix) <- data$axis1
data_matrix <- t(data_matrix)

# Run cytotrace on data, subsampling 1000 cells at a time
results <- CytoTRACE(data_matrix, ncores = 16)

# Make data frames of results and save them
results_cells <- data.frame(
    results$CytoTRACE,
    results$CytoTRACErank,
    results$GCS,
    results$Counts
    )
colnames(results_cells) <- c("CytoTRACE", "CytoTRACErank", "GCS", "Counts")
results_genes <- data.frame(
    results$cytoGenes,
    results$gcsGenes
    )
colnames(results_genes) <- c("cytoGenes", "gcsGenes")
# Save results
write.csv(results_cells, "analysis/raw_counts_cytoTrace_cell_data.csv")
write.csv(results_genes, "analysis/raw_counts_cytoTrace_gene_data.csv")
write.csv(
    results$exprMatrix,
    "analysis/raw_counts_cytoTrace_normalized_expression.csv"
    )
