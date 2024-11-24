use std::io;
use rand::Rng;
use std::cmp::Ordering;

fn main() {
    println!("Guess the number!");
    let secret_number = rand::thread_rng().gen_range(1..=10);
    loop {
        println!("Please input your guess.");
        let mut guess = String::new();
        io::stdin()
            .read_line(&mut guess)
            .expect("Failed to read line");
        let guess: u32 = guess.trim().parse().expect("Please type a number!");
        println!("You guessed: {guess}");
        match guess.cmp(&secret_number) {
            Ordering::Less => println!("Guess a higher numer!"),
            Ordering::Greater => println!("Guess a lower number!"),
            Ordering::Equal => {
                println!("You win!!!");
                break;
            }
        }
    }
}