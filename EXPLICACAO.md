# EXPLICACAO PATTERN MODE

## exemplo de comando

> $ JOSS_gen_netCDF.py -p "%Y%m%d" -d "01/08/2022"

## O que faz:

    Recebe o parâmetro -d e trata ele como uma data. Temos então datetime(year=2022,month=8,day=1).

    Gera 3 variáveis temporárias
        d0 = datetime(year=2022,month=8,day=1)
        d1 = datetime(year=2022,month=8,day=1) + day
        d2 = datetime(year=2022,month=8,day=1) - day

    Usa o valor recebido pelo parâmetro -p como um formatador de datetime. Assim formata d0, d1 e d2 como strings auxiliares. Veja:
        d0 = "20220801"
        d1 = "20220802"
        d2 = "20220731"

    Busca todos os arquivos no diretório de input, mas retorna na lista files, apenas aqueles arquivos cujo nome atenda aos critérios:
        1. nome de arquivo termina com a extensão especificada no veriables_info.json
        2. nome de arquivo contém alguma das string d0, d1 ou d2.

    A lista files é utilizada para ler os arquivos. Assim só lês os arquivos de interesse.

## Importante notar então:

    A. Parâmetro -p
    
        Deve ser passado o formato que a data é registrada no nome dos arquivos que estão colocados no diretório input.
        Por exemplo, para os arquivos:
            RD-20220731-215400.txt
            RD-20220801-215400.txt
            RD-20220802-215400.txt
        
        Veja que em RD-20220801-215400.txt
                       ^^^^^^^^
                    Data está aqui

        O formato da data acima é YYYYMMDD
        Porém é necessário passar esse formato segundo as convenções do python strftime. Ver detalhes no link: https://strftime.org/
        Assim deveríamos passar como valor para o parâmetro -p -> %Y%m%d

    B. Parâmetro -d

        Determina para qual dia vamos ler um dia antes e depois.
        É necessário passar um parâmetro -d sempre que usar o parâmetro - p