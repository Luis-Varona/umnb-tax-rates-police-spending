---@diagnostic disable: undefined-global
function Str(el)
  local text = el.text
  if text:find("\u{00A0}") then
    return pandoc.RawInline('latex', text:gsub("\u{00A0}", "\\hspace{0.25em}"))
  end
  return el
end
