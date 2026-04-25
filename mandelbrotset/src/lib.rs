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
        fn __contains__(&self, c: &Bound<PyComplex>) -> bool {
            self.stability(c, true, None) == 1f32
        }

        fn stability(&self, c: &Bound<PyComplex>, smooth: bool, clamp: Option<bool>) -> f32 {
            let clamp = clamp.unwrap_or(true);
            let stable = self.get_iteration_count(c, smooth) / (self.max_iteration as f32);
            return if clamp {
                0f32.max(stable.min(1f32))
            } else {
                stable
            };
        }
        fn get_iteration_count(&self, c: &Bound<PyComplex>, smooth: bool) -> f32 {
            // Zo vermijden we externe libraries te gaan gebruiken voor complexe getallen
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
                let magnitude = (z_re.powi(2) + z_im.powi(2)).sqrt(); // abs(z)
                if magnitude > (self.escape_radius as f32) {
                    return if smooth {
                        (iteration + 1) as f32 - magnitude.log2()
                    } else {
                        iteration as f32
                    };
                }
            }
            self.max_iteration as f32
        }
    }
}
