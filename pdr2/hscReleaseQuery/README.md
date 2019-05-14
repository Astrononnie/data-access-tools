# Command line interface to SQL Database

## Basic Usage

```sh
echo "SELECT now();" > 1.sql
python hscReleaseQuery3.py --user $YOUR_ID 1.sql --format csv > 1.csv
```

## Advanced Usage
```
usage: hscReleaseQuery3.py [-h] --user USER [--release-version {pdr1,pdr2}]
                           [--delete-job] [--format {csv,csv.gz,sqlite3,fits}]
                           [--nomail] [--password-env PASSWORD_ENV]
                           [--preview] [--skip-syntax-check]
                           [--api-url API_URL]
                           sql-file

positional arguments:
  sql-file              SQL file

optional arguments:
  -h, --help            show this help message and exit
  --user USER, -u USER  specify your account name (default: None)
  --release-version {pdr1,pdr2}, -r {pdr1,pdr2}
                        specify release version (default: pdr2)
  --delete-job, -D      delete the job you submitted after your downloading
                        (default: False)
  --format {csv,csv.gz,sqlite3,fits}, -f {csv,csv.gz,sqlite3,fits}
                        specify output format (default: csv)
  --nomail, -M          suppress email notice (default: False)
  --password-env PASSWORD_ENV
                        specify the environment variable that has password as
                        its content (default: HSC_SSP_CAS_PASSWORD)
  --preview, -p         quick mode (short timeout) (default: False)
  --skip-syntax-check, -S
                        skip syntax check (Use if you get 502: Proxy Error)
                        (default: False)
  --api-url API_URL     for developers (default: https://hsc-
                        release.mtk.nao.ac.jp/datasearch/api/catalog_jobs/)
```