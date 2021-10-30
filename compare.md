1. Start the cursor at the start of each file.
2. loop
   1. IF the characters are the same:
      1. increment both cursors
      2. skip
   2. IF the characters are different:
      1. read ahead until characters line up again (ex. 1 line)
      2. scroll old cursor to new position (addition) or vice versa (removal)
      3. mark new
      4. skip