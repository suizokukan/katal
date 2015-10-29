rm -rf faked/target
rm -rf faked/src2
cp -r faked/src faked/src2
./katal/katal.py --new=faked/target --mute
cp faked/katal.ini faked/target/.katal
cd faked/target
../../katal/katal.py --add --move --strictcmp
../../katal/katal.py --addtag=goose --to=*5.py
../../katal/katal.py --addtag=tree --to=*9.py
../../katal/katal.py --addtag=pink --to=*1*.py
../../katal/katal.py --rmnotag
rm 12.py
rm 14.py
../../katal/katal.py --cleandbrm
../../katal/katal.py --rmtags --to=10.py
../../katal/katal.py --findtag=goose
../../katal/katal.py --settagsstr="red;marble" --to=13.py
../../katal/katal.py -ti