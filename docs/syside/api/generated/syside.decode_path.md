<div id="syside-decode-path" class="section">

# syside.decode\_path[](#syside-decode-path "Link to this heading")

  - <span class="sig-name descname"><span class="pre">decode\_path</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">arg0</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.Url</span>](/v0.8.1/api/generated/syside.Url.md "syside.Url")</span>*, *<span class="n"><span class="pre">options</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n">[<span class="pre">syside.EncodingOpts</span>](/v0.8.1/api/generated/syside.EncodingOpts.md "syside.EncodingOpts")</span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">...</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><span class="pre">str</span></span></span>[](#syside.decode_path "Link to this definition")  
    Decode a filesystem path from a `Url`. This correctly handles Windows and Posix paths using `file://` scheme and returns other `Urls` as is.

</div>
