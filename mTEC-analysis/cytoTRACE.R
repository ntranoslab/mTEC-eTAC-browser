# Use conda python environment
Sys.setenv(RETICULATE_PYTHON = "/home/joe/anaconda3/envs/R_python/bin")

# Load libraries
library(rhdf5)
library(CytoTRACE)

# get list of files for batched count data
files <- list.files(
    path = "/mnt/iacchus/joe/processed_data/M_cell/batched_counts",
    full.names = TRUE,
    recursive = FALSE
    )

# Read in exported scVI data - rows are genes columns are cells
d <- list()
i <- 1
for (file in files){
    data <- h5read(file, "data")
    data_matrix <- data.frame(data$block0_values, row.names = data$axis0)
    colnames(data_matrix) <- data$axis1
    data_matrix <- t(data_matrix)
    file_name <- tail(strsplit(file, "/")[[1]], 1)
    d[[i]] <- data_matrix
    i <- i + 1
}

# Run cytotrace on data, subsampling 1000 cells at a time
results <- iCytoTRACE(d, ncores = 16)

# Make data frames of results and save them
results_cells <- data.frame(
    results$CytoTRACE,
    results$CytoTRACErank,
    results$GCS,
    results$Counts
    )
colnames(results_cells) <- c("CytoTRACE", "CytoTRACErank", "GCS", "Counts")
results_genes <- data.frame(results$cytoGenes)
colnames(results_genes) <- c("cytoGenes")
# Save results
write.csv(results_cells, "/home/joe/Repositories/mTEC-eTAC-atlases/mTEC-analysis/analysis/raw_counts_cytoTrace_cell_data.csv")
write.csv(results_genes, "/home/joe/Repositories/mTEC-eTAC-atlases/mTEC-analysis/analysis/raw_counts_cytoTrace_gene_data.csv")
write.csv(
    results$exprMatrix,
    "/home/joe/Repositories/mTEC-eTAC-atlases/mTEC-analysis/analysis/raw_counts_cytoTrace_normalized_expression.csv"
    )
