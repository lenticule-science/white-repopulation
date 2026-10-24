-- Render paper.yaml's people, disclosures and declarations into the document,
-- so the printed title page and the citation metadata share one source.

local stringify = pandoc.utils.stringify

local function person_name(person)
  if person.name then return stringify(person.name) end
  return stringify(person.given) .. " " .. stringify(person.family)
end

local function para(text)
  return pandoc.Para(pandoc.read(text, "markdown").blocks[1].content)
end

function Meta(meta)
  local authors = pandoc.List()
  for _, person in ipairs(meta.authors or {}) do
    local label = person_name(person)
    if person.affiliation then label = label .. " (" .. stringify(person.affiliation) .. ")" end
    authors:insert(pandoc.MetaInlines(pandoc.Inlines(label)))
  end
  meta.author = pandoc.MetaList(authors)
  if meta.version then
    meta.date = pandoc.MetaInlines(pandoc.Inlines("Version " .. stringify(meta.version) .. ", " .. stringify(meta.status or "")))
  end
  return meta
end

function Pandoc(doc)
  local meta = doc.meta
  local blocks = pandoc.List()
  blocks:insert(pandoc.Header(1, "Declarations", pandoc.Attr("declarations", {"unnumbered"})))

  local credits = pandoc.List()
  for _, person in ipairs(meta.authors or {}) do
    local text = "**" .. person_name(person) .. "**, " .. stringify(person.role or "")
    if person.disclosure then text = text .. ". " .. stringify(person.disclosure) end
    credits:insert({para(text)})
  end
  for _, person in ipairs(meta.acknowledgements or {}) do
    credits:insert({para("Acknowledged: **" .. stringify(person.name) .. "**, " .. stringify(person.role) .. ".")})
  end
  blocks:insert(pandoc.Header(2, "Authorship and AI disclosure", pandoc.Attr("", {"unnumbered"})))
  blocks:insert(pandoc.BulletList(credits))
  if meta["ai-disclosure"] then blocks:insert(para(stringify(meta["ai-disclosure"]))) end

  local sections = {
    {"Ethics", meta.ethics},
    {"Funding", meta.funding or "None declared."},
    {"Conflicts of interest", meta["conflicts-of-interest"] or "None declared."},
  }
  for _, section in ipairs(sections) do
    blocks:insert(pandoc.Header(2, section[1], pandoc.Attr("", {"unnumbered"})))
    blocks:insert(para(stringify(section[2])))
  end

  if meta.care then
    blocks:insert(pandoc.Header(2, "Indigenous data governance (CARE)", pandoc.Attr("", {"unnumbered"})))
    local items = pandoc.List()
    for _, key in ipairs({"collective-benefit", "authority-to-control", "responsibility", "ethics"}) do
      if meta.care[key] then items:insert({para("**" .. key:gsub("-", " ") .. ".** " .. stringify(meta.care[key]))}) end
    end
    blocks:insert(pandoc.BulletList(items))
  end

  blocks:insert(pandoc.Header(2, "Data and code availability", pandoc.Attr("", {"unnumbered"})))
  blocks:insert(para("All records, derived tables, analysis code and build provenance are in " ..
    stringify(meta["repository-code"]) .. " under the licenses declared in its REUSE.toml: text and data " ..
    stringify(meta.license.text) .. ", code " .. stringify(meta.license.code) .. ". " .. stringify(meta.license["third-party"])))

  -- Declarations precede the consolidated bibliography (the #refs div).
  local out, placed = pandoc.List(), false
  for _, block in ipairs(doc.blocks) do
    if not placed and block.t == "Header" and block.identifier == "appendix-b" then
      out:extend(blocks)
      placed = true
    end
    out:insert(block)
  end
  if not placed then out:extend(blocks) end
  return pandoc.Pandoc(out, meta)
end
