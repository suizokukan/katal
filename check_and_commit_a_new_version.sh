echo "=== Katal ==="
echo "=== this a bunch of various tests to be executed before committing a new version ==="

#-------------------------------------------------------------------------------
echo
echo    "  = next step : $ pylint katal.py"
read -p "  = go on ? ('y' to continue) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

pylint katal/katal.py

#-------------------------------------------------------------------------------
echo
echo    "  = next step : $ pylint setup.py"
read -p "  = go on ? ('y' to continue) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

pylint setup.py

#-------------------------------------------------------------------------------
echo
echo    "  = next step : $ pylint tests/tests.py"
read -p "  = go on ? ('y' to continue) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

pylint tests/tests.py


#-------------------------------------------------------------------------------
echo
echo    "  = next step : $ nosetests"
read -p "  = go on ? ('y' to continue) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

nosetests

#-------------------------------------------------------------------------------
echo
echo    "  = next step : $ python setup.py sdist bdist_wheel register -r test"
read -p "  = go on ? ('y' to continue) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi
    
python setup.py sdist bdist_wheel register -r test

#-------------------------------------------------------------------------------
echo
echo    "  = next step : $ python setup.py sdist bdist_wheel upload -r test"
read -p "  = go on ? ('y' to continue) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

python setup.py sdist bdist_wheel upload -r test

#-------------------------------------------------------------------------------
echo
echo    "  = next step : $ python setup.py sdist bdist_wheel register -r pypi"
read -p "  = go on ? ('y' to continue) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi
    
python setup.py sdist bdist_wheel register -r pypi

#-------------------------------------------------------------------------------
echo
echo    "  = next step : $ python setup.py sdist bdist_wheel upload -r pypi"
read -p "  = go on ? ('y' to continue) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

python setup.py sdist bdist_wheel upload -r pypi

#-------------------------------------------------------------------------------
echo
echo    "  = next step : $ sudo pip uninstall katal"
read -p "  = go on ? ('y' to continue) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

sudo pip uninstall katal

#-------------------------------------------------------------------------------
echo
echo    "  = next step : $ sudo pip install katal"
read -p "  = go on ? ('y' to continue) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

sudo pip install katal

#-------------------------------------------------------------------------------
echo
echo    "  = next step : $ katal --version"
read -p "  = go on ? ('y' to continue) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

katal --version

#-------------------------------------------------------------------------------
echo
echo    "  = next step : $ git commit -a"
read -p "  = go on ? ('y' to continue) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

git commit -a
