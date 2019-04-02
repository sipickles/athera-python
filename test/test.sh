# Usage: PYTHON_VERSION=3.7 ./test.sh [api|sync]

if [ -z ${PYTHON_VERSION+x} ]; then 
    echo "PYTHON_VERSION is unset (eg: 3.7)"; 
    exit 1
fi

source settings.sh
source creds.sh

python$PYTHON_VERSION -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$PYTHONPATH:$(pwd)/..
nose2 -v --plugin nose2.plugins.junitxml --plugin refresh_token_plugin --junit-xml $1
deactivate
