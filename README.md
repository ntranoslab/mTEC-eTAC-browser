# mTEC-eTAC-atlases
**Welcome!**
This is our [single cell analyzer](http://gardner-lab-computer:8050/) for our data on *Aire*-expressing cells in the thymus, lymph nodes, and more.

---
## Overview
This *Aire*-expressing Cell Atlas is a web application that lets users easily view UMAPs and tSNEs of compiled data of cells that reside in the thymus and secondary lymphoid organs. This is generated from both our and colleagues' single cell sequencing data.

### Thymus
This tab leads to a page with vizualizations of our thymus cell population, focusing on our medullary thymic epitelial cell data.
The first row of graphs is a UMAP of the single cell data of the thymus with a heat map of the expression of the selected gene (left) and the same UMAP showing the cell types within the data (right). 
One can change the selected gene to view, the genotype of the data, which dataset the data is pulling from, dataset for cell types, whether to view counts or normalized data, and change the color map and scale, including changing the max and min of the color bar and resetting the scale max and min to the 99th and 1st percentile of the data.

The second row of graphs is for comparing UMAPs of differing genotypes within our data, where the genotype displayed on the left graph is the reference genotype.
The color map and scale is based off of the reference genotype data (this includes the 99th and 1st percentile).
One can easily change genotypes or swap reference (left) and comparison (right) genotype. Like the first row of graphs, one can also change the selected gene.

### Lymph Nodes
This page contains vizualizations of our single cell data within the lymph nodes, primarily focusing on extrathymic *Aire*-expressing cells.
The selected gene and colormap and scale can be changed.
The percentiles are based off of the 1st and 99th percentile of the selected gene from the single cell lymph node data.

---
## Cheat Sheet
*Options*:
- Gene: Change selected gene
- Dataset: Change dataset
- Genotype: Change selected genotype within dataset
- Dataset for cell types: Choose which cell types to view
- Expression data: Choose to view raw counts or normalized data
- Dot size: Change dot size of points on UMAPs/tSNEs
- Color Map: Change color map color
- Scale: Adjust color scale maximum and minimum
- Percentiles: Reset scale to 1st or 99th percentile of selected gene value expresison
- Swap Button: Swap left and right genotypes (where scale and percentiles are based on the left graph)
- Cell type annotations: Choose which cell list to view in cell type graph

---
## Implementation
Coming soon: the web application will run online using an AWS EC2 instance with its dataset in a MySQL RDS, a relational database aws service.

***Hope you enjoy!***
