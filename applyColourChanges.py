import re
import json
import os
import shutil

#TODO: Fix \\w* matching colour name but not hex colour

def specialEscape(inString, chars=[".", "{", "}"]):
    """Adds escape characters in front of every character in chars in inString
    """
    charList = [
        entry
        if entry not in chars
        else "\{}".format(entry)
        for entry in inString
    ]
    return "".join(charList)

def changeCSSProperty(filepath, prop, prevVal, newVal):
    """Changes a css property (prop) from prevVal to newVal in filename using regex
    """
    # Add escape characters to all literal regexes
    prop = specialEscape(prop)
    prevVal = specialEscape(prevVal)
    newVal = specialEscape(newVal)

    # Open file
    with open(filepath) as f:
        lines = f.readlines()

    # Get line index of current property
    m = re.compile(prop)
    lineIdx = [idx for idx, line in enumerate(lines) if re.search(m, line) != None][0]

    # Create matches for closing bracket and desired property
    m_closingBracket = re.compile("\}")
    m_property = re.compile(prevVal)

    # Define maximum number of iterations to prevent while(true) loop
    MAX_MATCH_LEN = 30
    # Iterate over line(s) containing the property, sub line if the property is found
    # This is done to deal with the properties either being in the same line or lines following the original match
    for i in range(lineIdx, lineIdx + MAX_MATCH_LEN):
        # Replace desired property
        lines[i] = re.sub(m_property, newVal, lines[i])
        # Break out of loop if we detect the closing bracket
        if re.match(m_closingBracket, lines[i]) != None:
            break

    # Save edited file
    with open(filepath, "w") as f:
        for line in lines:
            f.write(line)

def createFileBackup(filepath, scriptpath):
    """Creates a copy of the file at filepath in a local ./backup folder
    """
    # Create backup directory if it doesn't exist yet
    backupdir = os.path.join(scriptpath, "backup")
    if not os.path.isdir(backupdir): os.mkdir(backupdir)
    # Extract filename from filepath and check if file exists
    filename = os.path.basename(filepath)
    # Check if file already exists in backup folder
    backupfiles = [
        f 
        for f in os.listdir(backupdir) 
        if os.path.isfile(os.path.join(backupdir, f))
    ]
    # Only create backup if it doesn't exist yet
    if filename not in backupfiles:
        shutil.copy(filepath, backupdir)

def main():
    ## Get path of python file location
    # Check for NameError in case we are running interactively
    try:
        scriptpath = os.path.dirname(os.path.realpath(__file__))
    except NameError:
        scriptpath = "."

    # Open json defining colours and parse json format
    with open(os.path.join(scriptpath, "colours.json")) as f:
        data = json.loads(f.read())

    # Set function arguments to None for checking the json as we go
    filepath = prop = prevVal = newVal = None

    # Iterate over entries we want to change
    # The config is stored in global variables each time to buffer previous entries
    # This approach allows for repeating entries (e.g. filepath) to be omitted in the json
    for entry in data:
        try: filepath = entry["filepath"]
        except KeyError: pass
        try: prop = entry["prop"]
        except KeyError: pass
        try: prevVal = entry["prevVal"]
        except KeyError: pass
        try: newVal = entry["newVal"]
        except KeyError: pass

        assert filepath != None, "No filepath specified for entry \n{}".format(entry)
        assert prop != None, "No property specified for entry \n{}".format(entry)
        assert prevVal != None, "No prevVal specified for entry \n{}".format(entry)
        assert newVal != None, "No newval specified for entry \n{}".format(entry)

        # At this point, we can be sure that all arguments are present
        # Check if file at filepath actually exists before proceeding
        assert os.path.isfile(filepath), "Specified file {} does not exist".format(filepath)

        # Create a local backup if not already present and call css property changing function
        createFileBackup(filepath, scriptpath)
        changeCSSProperty(filepath, prop, prevVal, newVal)

if __name__ == "__main__":
    main()
