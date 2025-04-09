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


local function delete_placeholder(emph)
  local text = pandoc.utils.stringify(emph)
  local pattern = "^%[.+ will appear here in the PDF%.%]$"

  if text:match(pattern) then
    return {}
  end

  return emph
end


local function uncomment_latex(raw_block)
  local text = raw_block.text
  local pattern = "^%s*<!%-%-%s*```{=latex}[\n\r]*(.-)[\n\r]*```%s*%-%->%s*$"

  if text:match(pattern) then
    return pandoc.RawBlock("latex", text:gsub(pattern, "%1"))
  end

  return raw_block
end


local function start_references(doc)
  local doc_blocks = doc.blocks

  for i = #doc_blocks, 1, -1 do
    local block = doc_blocks[i]

    if block.t == "Div" and block.attr.classes:includes("references") then
      local references_header = pandoc.Header(1, "References")
      table.insert(doc_blocks, i, references_header)
      return doc
    end
  end

  io.stderr:write("Error: No 'References' section found in the document.\n")
  os.exit(1)
end


local function move_appendix(doc)
  local doc_blocks = doc.blocks
  local appendix_blocks = {}
  local indices_remove = {}
  local in_appendix = false

  for i, block in ipairs(doc_blocks) do
    if block.t == "Header" and block.level == 1 then
      if block.content[1].text == "Appendix" then
        in_appendix = true
      elseif in_appendix then
        break
      end
    end

    if in_appendix then
      table.insert(appendix_blocks, block)
      table.insert(indices_remove, i)
    end
  end

  for i = #indices_remove, 1, -1 do
    table.remove(doc_blocks, indices_remove[i])
  end

  if #appendix_blocks > 0 then
    local newpage_break = pandoc.RawBlock("latex", "\\newpage")
    table.insert(doc_blocks, newpage_break)

    for _, block in ipairs(appendix_blocks) do
      table.insert(doc_blocks, block)
    end
  end

  return doc
end


return {
  Str = replace_nbsp,
  Emph = delete_placeholder,
  RawBlock = uncomment_latex,
  Pandoc = function (doc)
    return move_appendix(start_references(doc))
  end
}
