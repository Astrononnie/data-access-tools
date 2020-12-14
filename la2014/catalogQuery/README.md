# Command line interface to SQL Database
This tool allows you to send a query and retrieve data from your terminal.  This will be useful for sequential data retrieval.

## Basic Usage

```sh
echo "SELECT now();" > 1.sql
python hscReleaseQuery.py --user $YOUR_ID 1.sql --format csv > 1.csv
```

## Advanced Usage
```
usage: hscSspQuery.py [-h] --user USER [--release-version {hscla}]
                       [--delete-job]
                       [--format {csv,csv.gz,sqlite3,fits,numpygres-fits,fast-fits}]
                       [--nomail] [--password-env PASSWORD_ENV] [--preview]
                       [--skip-syntax-check] [--api-url API_URL]
                       [--login-url LOGIN_URL]
                       sql-file

positional arguments:
  sql-file              SQL file

optional arguments:
  -h, --help            show this help message and exit
  --user USER, -u USER  specify your account (default: None)
  --release-version {hscla}, -r {hscla}
                        specify release version (default: hscla)
  --delete-job, -D      delete the job you submitted after your downloading
                        (default: False)
  --format {csv,csv.gz,sqlite3,fits,numpygres-fits,fast-fits}, -f {csv,csv.gz,sqlite3,fits,numpygres-fits,fast-fits}
                        specify output format (default: csv)
  --nomail, -M          suppress email notice (default: False)
  --password-env PASSWORD_ENV
                        specify the environment variable which contains the
                        password (default: HSC_LA_PASSWORD)
  --preview, -p         quick mode (short timeout) (default: False)
  --skip-syntax-check, -S
                        skip syntax check (default: False)
  --api-url API_URL     for developers (default: https://hscla.mtk.nao.ac.jp/d
                        atasearch/api/catalog_jobs/)
  --login-url LOGIN_URL
                        for developers (default:
                        https://hscla.mtk.nao.ac.jp/account/api/session)

```