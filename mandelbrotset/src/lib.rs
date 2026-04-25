use pyo3::prelude::*;

/// A Python module implemented in Rust.
#[pymodule]
mod mandelbrotset {
    use pyo3::{prelude::*, types::PyComplex};

    #[pyclass]
    struct MandelbrotSet {
        escape_radius: u16,
        max_iteration: u16,
    }
    #[pymethods]
    impl MandelbrotSet {
        #[new]
        fn new(escape_radius: u16, max_iteration: u16) -> Self {
            Self {
                escape_radius,
                max_iteration,
            }
        }
        fn get_iteration_count(&self, c: &Bound<PyComplex>) -> u16 {
            let mut z_re: f32 = 0f32;
            let mut z_im: f32 = 0f32;
            let (c_re, c_im): (f32, f32) = (
                c.getattr("real").unwrap().extract().unwrap(),
                c.getattr("imag").unwrap().extract().unwrap(),
            );

            for iteration in 0..self.max_iteration {
                let new_z_re = z_re.powi(2) - z_im.powi(2) + c_re;
                let new_z_im = 2f32 * z_re * z_im + c_im;
                z_re = new_z_re;
                z_im = new_z_im;
                if (z_re.powi(2) + z_im.powi(2)).sqrt() > (self.escape_radius as f32) {
                    return iteration;
                }
            }
            self.max_iteration
        }
    }
}
