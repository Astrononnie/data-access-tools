# Postage Stamps in Color
If you want postage-stamps of your objects in color, you can upload an object list with this tool.

## Basic Usage
```sh
cat > coords.txt <<EOT
# ra         dec             outfile(optional)
4.62630      16.44671        a.png
4.63742      16.44747        b.png
4.62537      16.44345        c.png
4.65146      16.44694        d.png
4.64854      16.44695        e.png
4.65057      16.44706        f.png
4.62701      16.44535        g.png
4.65151      16.44745        h.png
4.63186      16.44911        i.png
4.63830      16.44271        j.png
EOT

python colorPostage.py --user YOUR_ACCOUNT --outDir pngs coords.txt
```

## Advanced Usage
```
usage: colorPostage.py [-h] --outDir OUTDIR --user USER [--filters FILTERS FILTERS FILTERS] [--fov FOV] [--rerun {la2014}] [--color {hsc,sdss}] input

positional arguments:
  input

optional arguments:
  -h, --help            show this help message and exit
  --outDir OUTDIR, -o OUTDIR
  --user USER, -u USER
  --filters FILTERS FILTERS FILTERS, -f FILTERS FILTERS FILTERS
  --fov FOV
  --rerun {la2014}
  --color {hsc,sdss}
```