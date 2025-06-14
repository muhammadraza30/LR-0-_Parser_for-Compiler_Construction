// Invalid control structures
agar x > 0 {   // Missing parentheses
    dikhao("Error");
}

jabtak true {  // Missing parentheses
    dikhao("Loop");
}

tabtak i = 0; i < 10; i++) {  // Invalid for loop syntax
    dikhao(i);
}