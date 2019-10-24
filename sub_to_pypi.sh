source activate py35

python setup.py sdist
python setup.py bdist_wheel
python setup.py bdist_wheel --universal

twine upload  --skip-existing dist/* && mv dist/GRID_LRT-* dist/old_releases/

source deactivate
