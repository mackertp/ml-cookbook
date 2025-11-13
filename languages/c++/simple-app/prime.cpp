/**
* A generic C++ example - how to find a prime number.
* 
* @author Preston Mackert
*/

// -------------------------------------------------------------- //
// abstractions
// -------------------------------------------------------------- //

#include <iostream>


// -------------------------------------------------------------- //
// functions
// -------------------------------------------------------------- //

int main() {
    // instantiate variables and collect user's input
    int i, n;
    bool is_prime = true;
    std::cout << "Enter a positive integer: ";
    std::cin >> n;
    
    // 0 and 1 are not prime, despite following rule
    if (n == 0 || n == 1) {
        is_prime = false;
    }
    for (i = 2; i <= n/2; ++i) {
        if (n % i == 0) {
            is_prime = false;
            break;
        }
    }
    
    // output for the user
    if (is_prime)
        std::cout << n << " is a prime number";
    else
        std::cout << n << " is not a prime number";
    
    // program executed successfully
    return 0;
}