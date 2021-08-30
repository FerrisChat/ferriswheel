use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use pyo3::PyErr;
use reqwest;
use reqwest::Error;

#[pyclass]
pub struct _HTTPClient {
    pub client: reqwest::Client,
    pub MAX_RETRIES: u8,
}

enum RequestReturnType {
    String(String),
    U16(u16),
}

// impl std::convert::From<Error> for PyErr {
//     fn from(e: Error) -> PyErr {
//         PyException::new_err(e.to_string());
//     }
// }

impl _HTTPClient {
    async fn _request(
        &self,
        url: &str,
        method: &str,
        body: Option<&str>,
    ) -> Result<RequestReturnType, reqwest::Error> {
        let mut _method = method.to_string();
        for tries in 0..self.MAX_RETRIES {
            let body = body.unwrap_or("").to_string();
            let method = reqwest::Method::from_bytes(_method.as_bytes()).unwrap();
            let response = self.client.request(method, url).body(body).send().await?;
            let status = response.status();
            if status.is_success() {
                return Ok(RequestReturnType::String(response.text().await?.clone()));
            }
            if status.is_client_error() {
                return Ok(RequestReturnType::U16(status.as_u16().clone()));
            }
            if status.is_server_error() {
                if tries == 1 {
                    return Ok(RequestReturnType::U16(status.as_u16().clone()));
                }
                continue;
            }
        }

        unreachable!();
    }
}
#[pymethods]
impl _HTTPClient {
    #[new]
    fn new(user_agent: &str) -> Result<Self, reqwest::Error> {
        Ok(_HTTPClient {
            client: reqwest::Client::builder().user_agent(user_agent).build()?,
            MAX_RETRIES: 3,
        })
    }

    fn request(&self, url: &str, method: &str, body: Option<&str>) -> PyResult<&PyAny> {
        Python::with_gil(|py| -> PyResult<&PyAny>{
            return pyo3_asyncio::tokio::future_into_py(py, self._request(url, method, body));
        })
    }
}

#[pymodule]
fn _http(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<_HTTPClient>()?;
    Ok(())
}
