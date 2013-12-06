
# if necessary, setup the dev bin scripts
if [[ "$PATH" == */.//bin* ]]
then
  echo "Adding ./bin to PATH"
  export PATH=$PATH:./bin
fi

# enable the virtual environment
source venv/bin/activate
