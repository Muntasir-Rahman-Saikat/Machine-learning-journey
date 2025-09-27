# #!/bin/bash

# PYTHON_SCRIPT="logger.py"

# #check the log file in every 20 seconds (we pass here seconds)
# INTERVAL=20 

# echo "Starting the log checker. Press Ctrl+C to stop."

# while true
# do
#     echo "Running the Python script to check for errors..."
#     python3 "$PYTHON_SCRIPT"
#     echo "Explicitely sleeping for $INTERVAL seconds..."
#     sleep $INTERVAL
# done

#!/bin/bash
PYTHON_SCRIPT='logger.py'
INTERVAL=10

echo "staring the log checker.Press Ctrl+C for termination"

while true
do
    echo "running the python script to check for errors"
    python3 "$PYTHON_SCRIPT"
    echo "Explicitely sleeping for interval seconds"
    sleep $INTERVAL
done
