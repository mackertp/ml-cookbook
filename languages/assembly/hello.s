/* 
* An assembly program for demonstration purposes.
* Run on Mac OS Silicon.
*
* @author: Preston Mackert   
*/

// ------------------------------------------------------------- //
// Compiling and running the program    
// ------------------------------------------------------------- //

/*
* Convert to an object file:
*   $ as hello.s -o hello.o
*
* Use linker to convert into an executable file named "app":
*   $ ld hello.o -o app -l System -syslibroot `xcrun -sdk macosx --show-sdk-path` -e _main -arch arm64
*
* Run application:
*   $ ./app
*/

.global _main
.align 2 // required for mac silicon

_main:
    b _pprint   

_pprint:
    mov X0, #1      // stdout
    adr X1, yomomma // address of string
    mov X2, #10     // nuber of bytes in the string
    mov X16, #4     // write to stdout 
    svc 0 

_reboot:
    mov X0, #1      // instant reboot 
    mov X16, #55    
    svc 0 

_terminate:
    mov X0, #0      // return 0
    mov X16, #1     // terminate
    svc 0           // syscall

// yo
yomomma: .ascii "your mom\n"

