<div id="json-labs" class="section">

# JSON <span class="sd-sphinx-override sd-badge sd-outline-primary sd-text-primary">Labs</span><a href="#json-labs" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Syside supports bi-directional JSON serialization.

<div id="export" class="section">

## Export<a href="#export" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

Serialization produces a mostly specification compliant JSON with a few minor differences:

- not all implicit elements are constructed which will fail for attributes that are defined as non-null in the standard JSON schema, e.g. <span class="pre">`Function::result`</span>;

- references can be serialized with relative <span class="pre">`@uri`</span> field for references to elements from other documents by passing <span class="pre">`include_cross_ref_uris=True`</span> (default) to <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json.dumps"><span class="pre"><code class="sourceCode python">json.dumps</code></span></a>. This brings JSON exports in-line with corresponding XMI exports used by the Pilot implementation where references are always exported as <span class="pre">`<relative`</span>` `<span class="pre">`URI>#<element`</span>` `<span class="pre">`id>`</span>. Additionally, such exports enable much faster deserialization because cross references are transparent and do not require searching the world for their resolution.

  <div class="admonition note">

  Note

  A custom URI scheme to reference elements relative to their owning SysML packages (not the elements) may be added in the future as package manager support is implemented. This would remove the dependence on filesystem layout for deserialization.

  </div>

<div class="highlight-py notranslate">

<div class="highlight">

    json: str = syside.json.dumps(
        element, options=syside.SerializationOptions.minimal()
    )

</div>

</div>

<a href="/python/v0.8.4/syside/SerializationOptions.md" class="reference internal" title="syside.SerializationOptions"><span class="pre"><code class="sourceCode python">SerializationOptions</code></span></a> controls what gets serialized. Using <a href="/python/v0.8.4/syside/SerializationOptions.md" class="reference internal" title="syside.SerializationOptions.minimal"><span class="pre"><code class="sourceCode python">minimal</code></span></a> is recommended for most use cases.

<div class="admonition warning">

Warning

JSONs typically take 100-1000 times more space than the original textual notation even with minimal options and are opaque to human readers. Textual notation is recommended instead of JSON whenever possible.

</div>

</div>

<div id="import" class="section">

## Import<a href="#import" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

JSON deserialization (import) works on the same JSON files as were exported. However, in the interest of keeping the initial implementation simple there are a few limitations:

- root node is inferred as:

  - the first <span class="pre">`Namespace`</span> without an owning relationship,

  - the last ancestor of the first element in the array following either owning namespaces, owning related elements, or owning relationships,

  - the first element in the array otherwise;

- references to elements from other <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre"><code class="sourceCode python">Documents</code></span></a> may contain a <span class="pre">`@uri`</span> field. The URI of the <a href="/python/v0.8.4/syside/Document.md" class="reference internal" title="syside.Document"><span class="pre"><code class="sourceCode python">Document</code></span></a> model is deserialized into will be used to resolve relative URI references, otherwise an empty URI will be passed to the resolver callback;

- deserialization may be lossy because the specification dumps all owned elements into <a href="/python/v0.8.4/syside/Element.md" class="reference internal" title="syside.Element.owned_relationships"><span class="pre"><code class="sourceCode python">owned_relationships</code></span></a> and <a href="/python/v0.8.4/syside/Relationship.md" class="reference internal" title="syside.Relationship.owned_related_elements"><span class="pre"><code class="sourceCode python">owned_related_elements</code></span></a> attributes which lose the more fine grained information stored in the model by Syside. For example, <a href="/python/v0.8.4/syside/SendActionUsage.md" class="reference internal" title="syside.SendActionUsage"><span class="pre"><code class="sourceCode python">SendActionUsage</code></span></a> <span class="pre">`receiver`</span>, <span class="pre">`payload`</span>, and <span class="pre">`sender`</span> are all parameters to <a href="/python/v0.8.4/syside/ReferenceUsage.md" class="reference internal" title="syside.ReferenceUsage"><span class="pre"><code class="sourceCode python">ReferenceUsage</code></span></a>, only disambiguated by their relative position, so if one is missing the others may be deserialized into different members.

Note that deserialization ignores majority of fields present in the JSON schema, including all derived fields with the exception of <span class="pre">`name`</span> and <span class="pre">`shortName`</span>. Therefore users may wish to export JSONs with minimal export options to reduce memory usage and improve performance.

Currently, to support cyclical JSON imports, foreign references are not resolved eagerly and instead must be resolved after deserialization:

<div class="highlight-py notranslate">

<div class="highlight">

    result, document = syside.json.loads(
        model_json, "file:///home/user/test.sysml"
    )
    # ... collect all valid element ids for linking, e.g.
    map = syside.IdMap()
    map.insert_or_assign(result.document)  # and other documents
    # resolve pending foreign references
    report, success = result.link(map)

</div>

</div>

<a href="/python/v0.8.4/syside/DeserializedModel.md" class="reference internal" title="syside.DeserializedModel.link"><span class="pre"><code class="sourceCode python">DeserializedModel.link</code></span></a> accepts any callable <span class="pre">`(uri:`</span>` `<span class="pre">`str,`</span>` `<span class="pre">`element_id:`</span>` `<span class="pre">`UUID)`</span>` `<span class="pre">`->`</span>` `<span class="pre">`Element`</span>` `<span class="pre">`|`</span>` `<span class="pre">`None`</span>, not just <a href="/python/v0.8.4/syside/IdMap.md" class="reference internal" title="syside.IdMap"><span class="pre"><code class="sourceCode python">IdMap</code></span></a>. Note that for unowned references without <span class="pre">`@uri`</span> field, <span class="pre">`uri`</span> will be an empty string.

</div>

<div id="low-level" class="section">

## Low-level<a href="#low-level" class="headerlink" title="Link to this heading"><span class="nerd-font"></span></a>

High-level <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json.dumps"><span class="pre"><code class="sourceCode python">json.dumps</code></span></a> and <a href="/python/v0.8.4/syside/json//README.md" class="reference internal" title="syside.json.loads"><span class="pre"><code class="sourceCode python">json.loads</code></span></a> are built on top of low-level API for convenience. Performance of repeated JSON serializations can be improved using low-level API:

- Exporting model rooted at <span class="pre">`element:`</span>` `<span class="pre">`Element`</span>:

  <div class="highlight-py notranslate">

  <div class="highlight">

      writer = syside.JsonStringWriter()
      serializer = syside.Serializer()
      report: syside.SerdeReport[syside.Element] = serializer.accept(
          element, writer, options=syside.SerializationOptions.minimal()
      )
      output: str = writer.result

  </div>

  </div>

  Writer can be reused by calling <a href="/python/v0.8.4/syside/JsonStringWriter.md" class="reference internal" title="syside.JsonStringWriter.clear"><span class="pre"><code class="sourceCode python">.clear()</code></span></a>. <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.serialize"><span class="pre"><code class="sourceCode python">serialize</code></span></a> can be used in place of <a href="/python/v0.8.4/syside/Serializer.md" class="reference internal" title="syside.Serializer.accept"><span class="pre"><code class="sourceCode python">Serializer.accept</code></span></a> if performance is not a concern.

- Importing <span class="pre">`json_str:`</span>` `<span class="pre">`str`</span> into <span class="pre">`target_document:`</span>` `<span class="pre">`Document`</span>:

  <div class="highlight-py notranslate">

  <div class="highlight">

      reader = syside.JsonReader()
      deserializer = syside.Deserializer(target_document)
      with reader.bind(json_str) as contents:
          model: syside.DeserializedModel
          report: syside.SerdeReport[
              syside.DocumentSegment | str | syside.Element
          ]
          model, report = deserializer.accept(
              contents, syside.DESERIALIZE_STANDARD
          )

  </div>

  </div>

  <span class="pre">`reader`</span> can be reused by binding multiple times, but not recursively, foreign references need to be linked as in the previous <a href="#json-link" class="reference internal"><span class="std std-ref">section snippet</span></a>. <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.deserialize"><span class="pre"><code class="sourceCode python">deserialize</code></span></a> can be used in place of <a href="/python/v0.8.4/syside/Deserializer.md" class="reference internal" title="syside.Deserializer.accept"><span class="pre"><code class="sourceCode python">Deserializer.accept</code></span></a> if performance is not a concern. The last parameter <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.DESERIALIZE_STANDARD"><span class="pre"><code class="sourceCode python">DESERIALIZE_STANDARD</code></span></a> controls the attribute names that are used in deserialization. The former looks for standard defined <span class="pre">`camelCased`</span> attributes names, e.g. <span class="pre">`shortName`</span>, while <a href="/python/v0.8.4/syside//README.md" class="reference internal" title="syside.DESERIALIZE_INTERNAL"><span class="pre"><code class="sourceCode python">DESERIALIZE_INTERNAL</code></span></a> – <span class="pre">`snake_cased`</span> names that also match Python API naming convention, e.g. <span class="pre">`short_name`</span>.

</div>

</div>
