# Datamap Scripts

Este repositório contém scripts para gerar arquivos netCDF a partir de dados em formato `.trf` e também para gerar figuras a partir de arquivos netCDF. Abaixo estão descritos os comandos disponíveis para execução dos scripts.

## Gen netCDF

### Executar para todos os arquivos `.trf` no diretório `input/JOSS/data`
Gera um arquivo netCDF para cada dia que possuir dados.

```bash
python JOSS_gen_netCDF.py -s
```

### Executar para uma data específica
Gera um arquivo netCDF apenas com os dados da data especificada no comando.

```bash
python JOSS_gen_netCDF.py -s -d 31/01/2000
```

### Executar para arquivos listados em `files.txt`
Gera um arquivo netCDF para cada dia que possuir dados dos arquivos cujos nomes estão incluídos no arquivo `files.txt` no diretório `input/JOSS`.

```bash
python JOSS_gen_netCDF.py -l
```

### Executar para uma data específica de arquivos listados em `files.txt`
Gera um arquivo netCDF apenas com os dados da data especificada no comando para os arquivos listados em `files.txt`.

```bash
python JOSS_gen_netCDF.py -l -d 31/01/2000
```

## Gen Figures

### Executar para todos os arquivos netCDF no diretório `input/JOSS/data_figures`
Gera todas as figuras nos formatos PNG e HTML.

```bash
python JOSS_gen_figures.py -s
```

### Executar para todos os arquivos netCDF no formato PNG
Gera apenas as figuras no formato PNG.

```bash
python JOSS_gen_figures.py -s -p
```

### Executar para arquivos listados em `files_figures.txt`
Gera todas as figuras para os arquivos cujos nomes estão incluídos no arquivo `files_figures.txt` no diretório `input/JOSS`.

```bash
python JOSS_gen_figures.py -l
```

### Executar para arquivos listados em `files_figures.txt` no formato PNG
Gera apenas as figuras no formato PNG.

```bash
python JOSS_gen_figures.py -l -p
```

## Estrutura de Diretórios

- `input/JOSS/data/`: Contém os arquivos `.trf` para gerar netCDF.
- `input/JOSS/data_figures/`: Contém os arquivos `.nc` para gerar figuras.
- `input/JOSS/files.txt`: Lista de arquivos `.trf` a serem processados.
- `input/JOSS/files_figures.txt`: Lista de arquivos `.nc` a serem processados.
