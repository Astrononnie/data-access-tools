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

~/anaconda3/bin/python colorPostage.py --user michitaro.nike@gmail.com --outDir png3 ./coords.txt
