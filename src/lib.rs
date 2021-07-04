use jmespath::{Rcvar, Variable};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::PyObjectProtocol;

/// A compiled JMESPath expression
///
/// Note that a compiled expression can't be accessed by another thread.
#[pyclass(module = "rjmespath")]
struct Expression {
    inner: jmespath::Expression<'static>,
}

impl Expression {
    #[inline]
    fn search_impl(&self, json: &str) -> Result<Rcvar, String> {
        let data = jmespath::Variable::from_json(json)?;
        self.inner
            .search(data)
            .map_err(|err| format!("JMESPath expression search failed: {}", err))
    }
}

#[pymethods]
impl Expression {
    /// Search the JSON with a compiled JMESPath expression
    fn search(&self, py: Python, json: &str) -> PyResult<PyObject> {
        let result = py
            .allow_threads(|| self.search_impl(json))
            .map_err(|err| PyValueError::new_err(err))?;
        Ok(rcvar_to_pyobject(py, result))
    }
}

#[pyproto]
impl PyObjectProtocol for Expression {
    fn __str__(&self) -> &str {
        self.inner.as_str()
    }

    fn __repr__(&self) -> String {
        self.inner.as_ast().to_string()
    }
}

fn rcvar_to_pyobject(py: Python, var: Rcvar) -> PyObject {
    match &*var {
        Variable::Null => py.None(),
        Variable::String(v) => v.into_py(py),
        Variable::Bool(v) => v.into_py(py),
        Variable::Number(v) => v.into_py(py),
        Variable::Array(v) => {
            let arr = PyList::new(py, v.iter().map(|x| rcvar_to_pyobject(py, x.clone())));
            arr.into_py(py)
        }
        Variable::Object(v) => {
            let dict = PyDict::new(py);
            for (k, v) in v {
                dict.set_item(k, rcvar_to_pyobject(py, v.clone()))
                    .expect("failed to set_item on PyDict");
            }
            dict.into_py(py)
        }
        Variable::Expref(_) => unimplemented!(),
    }
}

#[inline]
fn search_impl(expr: &str, json: &str) -> Result<Rcvar, String> {
    let expr =
        jmespath::compile(expr).map_err(|err| format!("Invalid JMESPath expression: {}", err))?;
    let data = jmespath::Variable::from_json(json)?;
    expr.search(data)
        .map_err(|err| format!("JMESPath expression search failed: {}", err))
}

/// Search the JSON with a JMESPath expression
#[pyfunction]
fn search(py: Python, expr: &str, json: &str) -> PyResult<PyObject> {
    let result = py
        .allow_threads(|| search_impl(expr, json))
        .map_err(|err| PyValueError::new_err(err))?;
    Ok(rcvar_to_pyobject(py, result))
}

/// Compiles a JMESPath expression
#[pyfunction]
fn compile(expr: &str) -> PyResult<Expression> {
    let inner = jmespath::compile(expr).map_err(|err| {
        let msg = format!("Invalid JMESPath expression: {}", err);
        PyValueError::new_err(msg)
    })?;
    Ok(Expression { inner })
}

/// Python bindings to Rust jmespath crate
#[pymodule]
fn rjmespath(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_class::<Expression>()?;
    m.add_function(wrap_pyfunction!(search, m)?)?;
    m.add_function(wrap_pyfunction!(compile, m)?)?;
    Ok(())
}
