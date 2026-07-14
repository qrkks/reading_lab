package main

import "fmt"

func add[T int | uint](a, b T) T {
	return a + b
}

func main() {
	fmt.Println(add(uint(2), 3))
}
