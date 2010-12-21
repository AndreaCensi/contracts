export PYTHONPATH=`pwd`:$PYTHONPATH 
sphinx-build $* -n -a -b html source website
