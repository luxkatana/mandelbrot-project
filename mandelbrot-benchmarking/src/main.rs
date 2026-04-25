use num::complex::Complex;
use std::time::Instant;
const MAX_ITERATION: u32 = 256;
const ESCAPE_RADIUS: i32 = 1000;
fn main() {
    let begin = Instant::now();
    for x in 0..512 {
        for y in 0..512 {
            let c: Complex<f32> = Complex::new((x - 256) as f32, (256 - y) as f32);
            get_iteration_count(c);
        }
    }

    let duration = {
        let end = Instant::now();
        end.duration_since(begin)
    };
    println!("Time taken: {}", duration.as_millis());
}
fn get_iteration_count(number: Complex<f32>) -> u32 {
    // number: c
    let mut z: Complex<f32> = Complex::new(0f32, 0f32);
    for iteration in 0..MAX_ITERATION {
        z = z * z + number;
        if z.re.abs() > ESCAPE_RADIUS as f32 {
            return iteration;
        }
    }
    MAX_ITERATION
}
