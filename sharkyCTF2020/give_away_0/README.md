# Give Away 0

- Genre pwn  

The first thing to do for this challenge was to check what kind of binary we were given.  

```sh
checksec 0_give_away
[*] '/Documents/ctf/sharky/pwn/giveaway0/0_give_away'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
file 0_give_away 
0_give_away: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=e0fb611b13ac822d3074696fb8bb10ea80c05882, not stripped
```

It was a 64 bit binary. NX was enabled so no shellcode for this challenge. I ran this binary to see what it did.
```sh
./0_give_away 
hello
```
It waited an input, and once I typed a message it just exited.   
To see the details of the binary I ran this with gdb.  

![image](https://user-images.githubusercontent.com/53568647/85538996-bf3c5180-b658-11ea-930f-90e3b7350be2.png)

By looking at the main function and vuln function, there was fgets call and a potential vulnerability.  
So I set a breake point at vuln+27, then ran the program.  

![image](https://user-images.githubusercontent.com/53568647/85539895-b0a26a00-b659-11ea-9ea8-30efa1c559dc.png)

I typed 32 'A's as an input, and the stack was now like this:  

![image](https://user-images.githubusercontent.com/53568647/85540063-e5162600-b659-11ea-8a84-a87c4960930d.png)  

![image](https://user-images.githubusercontent.com/53568647/85540547-784f5b80-b65a-11ea-8861-a9ff891669ce.png)  

At 0x7fffffffdd48, I found 0x004006ff, which was the return address. The size of the buffer from the top where 0x41 started to the return address was 0x7fffffffdd48 - 0x7fffffffdd20, 40 bytes.   
So if I could overwrite this return address to arbitrary address, I would call any function.   
This was confirmed by pattern_create and pattern_offset.  

![image](https://user-images.githubusercontent.com/53568647/85541941-eba59d00-b65b-11ea-92a2-149f49abcab9.png)  

![image](https://user-images.githubusercontent.com/53568647/85543705-a6826a80-b65d-11ea-9508-42e7a8e11981.png)

I conducted a further research and found an interesting function 'win_func'.  

![image](https://user-images.githubusercontent.com/53568647/85545460-4ee4fe80-b65f-11ea-828c-ff527e2ac083.png)

So I tried to inject this address with 40 'A's as an input.  
Fortunately,  ASLR was disabled for this challenge, I could easily get the win_func address.  

```sh
(python -c "print('a'*40 + '\xa7\x06\x40\x00' + '\x00'*4)";cat) | ./0_give_away 
```

![image](https://user-images.githubusercontent.com/53568647/85548004-d59adb00-b661-11ea-86fb-59c4ef90dbf7.png)

I could get a shell locally with the above command. So I wrote a python script to get a remote shell.  

![image](https://user-images.githubusercontent.com/53568647/85547694-7dfc6f80-b661-11ea-83ed-cfaab37771a7.png)

The flag was:  
shkCTF{#Fr33_fL4g!!_<3}


