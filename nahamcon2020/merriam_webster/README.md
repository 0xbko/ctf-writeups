# Merriam Webster

- Genre Scripting
- 125 points



Once connecting the server I saw a prompt:  
 'Can you tell me how many words here are NOT real words?'  
 with a list of words. 
  
It simply kept asking some questions, and I needed to send the answer back to the server.  
The list of questions are:
- Can you tell me how many words here are NOT real words?
- Can you tell me which words here are NOT real words IN CHRONOLOGICAL ORDER? Separate each by a space.  
- Can you tell me which words here are NOT real words IN ALPHABETICAL ORDER? Separate each by a space.
- Can you tell me how many words here ARE real words?
- Can you tell me which words here ARE real words IN CHRONOLOGICAL ORDER? Separate each by a space.
- Can you tell me which words here ARE real words IN ALPHABETICAL ORDER? Separate each by a space.  

These questions were given in random order and it was painful to deal with this iterative process manually for more than a few hundred times.

Note: Initially, I tried solving this task with python libraries (pyenchant, pyspellchecker), but did not work well. I finally figured out to use /usr/share/dict/words instead.  

Flag: flag{you_know_the_dictionary_so_you_are_hired}