echo "(01) rm -rf faked/target"
rm -rf faked/target

echo "(02) rm -rf faked/src2"
rm -rf faked/src2

echo "(03) cp -r faked/src faked/src2"
cp -r faked/src faked/src2

echo "(04) ./katal/katal.py --new=faked/target --mute"
./katal/katal.py --new=faked/target --mute

echo "(05) cp faked/katal.ini faked/target/.katal"
cp faked/katal.ini faked/target/.katal

echo "(06) cd faked/target"
cd faked/target

echo "(07) ../../katal/katal.py --add --move --strictcmp"
../../katal/katal.py --add --move --strictcmp

echo "(08) ../../katal/katal.py --addtag=goose --to=*5.py"
../../katal/katal.py --addtag=goose --to=*5.py

echo "(09) ../../katal/katal.py --addtag=tree --to=*9.py"
../../katal/katal.py --addtag=tree --to=*9.py

echo "(10) ../../katal/katal.py --addtag=pink --to=*1*.py"
../../katal/katal.py --addtag=pink --to=*1*.py

echo "(11) ../../katal/katal.py --rmnotag"
../../katal/katal.py --rmnotag

echo "(12) rm 12.py"
rm 12.py

echo "(13) rm 14.py"
rm 14.py

echo "(14) ../../katal/katal.py --cleandbrm"
../../katal/katal.py --cleandbrm

echo "(15) ../../katal/katal.py --rmtags --to=10.py"
../../katal/katal.py --rmtags --to=10.py

echo "(16) ../../katal/katal.py --findtag=goose"
../../katal/katal.py --findtag=goose

echo "(17) ../../katal/katal.py --settagsstr="red;marble" --to=13.py"
../../katal/katal.py --settagsstr="red;marble" --to=13.py

echo "(18) ../../katal/katal.py --findtag=pink --copyto=xyz"
../../katal/katal.py --findtag=pink --copyto=xyz

echo "(19) ../../katal/katal.py -ti"
../../katal/katal.py -ti

echo "(20) ../../katal/katal.py --whatabout 0.py"
../../katal/katal.py --whatabout 0.py
