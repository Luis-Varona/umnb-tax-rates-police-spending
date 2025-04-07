---@diagnostic disable-next-line: lowercase-global
pandoc = pandoc

local function replace_nbsp(el)
  local text = el.text
  local pattern = "\u{00A0}"
  local repl = "\\hspace{0.25em}"
  if text:find(pattern) then
    return pandoc.RawInline("latex", text:gsub(pattern, repl))
  end
  return el
end

local function delete_placeholder(el)
  local text = pandoc.utils.stringify(el)
  local pattern = "^%[.+ will appear here in the PDF%.%]$"
  if text:match(pattern) then
    return {}
  end
  return el
end

local function uncomment_latex(el)
  local text = el.text
  local pattern = "^%s*<!%-%-%s*```{=latex}[\n\r]*(.-)[\n\r]*```%s*%-%->%s*$"
  if text:match(pattern) then
    return pandoc.RawBlock("latex", text:gsub(pattern, "%1"))
  end
  return el
end

local function start_references(doc)
  local references_header = pandoc.Header(1, "References")
  for i = #doc.blocks, 1, -1 do
    local block = doc.blocks[i]
    if block.t == "Div" and block.attr.classes:includes("references") then
      table.insert(doc.blocks, i, references_header)
      return doc
    end
  end
  io.stderr:write("Error: No 'references' Div found in the document.\n")
  os.exit(1)
end

return {
  Str = replace_nbsp,
  Emph = delete_placeholder,
  RawBlock = uncomment_latex,
  Pandoc = start_references,
}
