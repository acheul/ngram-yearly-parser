/***
 Use a release file for python library.
 LINUX: use 'rustlib.so' file.
 MS WINDOWS: change 'rustlib.dll' file into 'rustlib.pyd' then use it.
*/


#[macro_use]
extern crate cpython;
 
use cpython::{Python, PyResult};
use std::collections::HashMap;

/// Parse a line into a vector of (year: u16, new_line(ngram+count): String)
/// ```
/// Ex:
///   input line: "This is a five gram\t1910,2,2\t1920,1,1\t1930,12,10"
///   result: [(1910, "This is a five gram\t2"), (1920, "This is a five gram\t1"), (1930, "This is a five gram\t12")]
/// ```
fn parse_line(_py: Python, line: &str) -> PyResult<Option<Vec<(u16, String)>>> {

  let mut line_split = line.split('\t');
  if let Some(ngram) = line_split.next() {

    let new_lines: Vec<(u16, String)> =
      line_split.filter_map(|ycc| {

        let mut ycc = ycc.split(',');
        if let Some(year) = ycc.next() {
          if let Ok(year) = year.parse::<u16>() {
            if let Some(match_count) = ycc.next() {
              let ngram_count = format!("{}\t{}", ngram, match_count);
              // let ngram_count = format!("{}\t{}\n", ngram, match_count);
              return Some((year, ngram_count));
            }
          }
        }
        None
      }).collect();
    return Ok(Some(new_lines))
  }
  Ok(None)
}

/// Collect lines into HashMap<year: u16, new_lines: Vec<String>>
/// ```
/// Ex:
///   input lines: vec![(1910, "This is a five gram\t2"), (1930, "This is a five gram\t1"), (1930, "This is the five gram\t12")]
///   result: {
///     1910: ["This is a five gram\t2"],
///     1930: ["This is a five gram\t1", "This is the five gram\t12"],
///   }
/// ```
fn collect_lines(_py: Python, lines: Vec<(u16, String)>) -> PyResult<HashMap<u16, Vec<String>>> {

  let mut map: HashMap<u16, Vec<String>> = HashMap::new();
  for (year, line) in lines.into_iter() {
    if let Some(lines) = map.get_mut(&year) {
      lines.push(line);
    } else {
      map.insert(year, vec![line]);
    }
  }

  Ok(map)
}


py_module_initializer!(rustlib, |py, module| {
  module.add(py, "__doc__", "This module is implemented in Rust")?;
  module.add(py, "parse_line", py_fn!(py, parse_line(line: &str)))?;
  module.add(py, "collect_lines", py_fn!(py, collect_lines(lines: Vec<(u16, String)>)))?;
  Ok(())
});