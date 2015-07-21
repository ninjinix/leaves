#!/usr/local/bin/ruby
require 'cgi'
require 'fileutils'
require 'base64'
#================================================================
def icgi
  $cgi ||= CGI.new
end

def cgip(s)
  icgi.params[s.to_s].first
end

def esc(s)
  s ? CGI.escapeHTML(s) : nil
end

def unesc(s)
  s ? CGI.unescapeHTML(s) : nil
end

def to64(s)
  encode64(s).gsub(/=+$/, '').gsub("\n", '').
    gsub('+', '-').gsub('/', '_')
end

def from64(s)
  s += '=' while s.size % 4 != 0
  decode64(s.gsub('-', '+').gsub('_', '/'))
end

def contentText(s)
  "Content-type: text/plean; charset=utf-8\n\n"+s
end

def contentJson(s)
  "Content-Type: application/json; charset=utf-8\n\n"+s
end

def s2json(s)
  '"'+s.gsub(/\r/,'\r').gsub(/\n/,'\n').gsub(/"/,'\"')+'"'
end

SCRIPT_NAME = File.basename(icgi.script_name)
#================================================================
SITE_NAME = 'Memo Cloud'
#----------------------------------------------------------------
CSS = <<EOD
<!--
html {-webkit-text-size-adjust:none;}
* {line-height: 120%; font-size: 100%;
  font-family: Consolas, 'Courier New', Courier, Monaco, monospace;}
body {margin: 0; padding: 0; background: #000 url(bg002.jpg) fixed;
  font-size: 12px; color: #ddd;}
a {color: #68a; text-decoration: none;}
p {padding: 0; margin: 1em 0;}

h1,h2 {font-weight: normal; margin: 0 0 0.5em 0; padding: 0;
  border-bottom: dashed 1px #8ac; color: #222;}
h2 {margin-top: 1em;}

table {margin: 0em; border-collapse: collapse;}
td {padding: 3px 6px; border: 1px solid #9ab;}

#header {
  background: rgba(255,255,255,0.85);
  margin-bottom: 5px;
  padding: 12px;
  color: #445;
}
#header input {padding: 0; margin: 0;
  background: #fff; color: #444; border: 1px solid #aac;}

.masonry {margin: 0 auto;}
.item {border-radius: 5px; background-color: rgba(255,255,255,0.85);
  margin: 5px; padding: 5px; width: 460px; color: #222;}

#txt {width: 98%; height: 25em; margin-bottom: 3px;
  background: rgba(0,0,0,0);
  border: 1px solid #aaa; color: #444;}
#write {padding: 0 10px; margin: 0 5px 0 0;}
#close {padding: 0 10px; margin: 0 5px 0 0;}

-->
EOD
#----------------------------------------------------------------
SCRIPT = <<EOD
<!--
var container = 0;
var masonry = 0;

function to64(s) {
  return Base64.encodeURI(s);
}
function from64(s) {
  return Base64.decode(s);
}
function ajaxPost(d, f) {
  $.ajax({
    type: "POST", scriptCharset: 'utf-8', dataType: "json", cache: false,
    url: "#{SCRIPT_NAME}", data: d, success: f,
    error: function(xhr, textStatus, errorThrown) { alert(textStatus); }
  });
}
function removeItem(v) {
  if (v == null) return;
  masonry.remove(v);
}
function prependItem(v) {
  if (v == null) return;
  container.insertBefore(v, container.firstChild);
  masonry.prepended(v);
}

function touchItem(s, isEdit) {
  removeItem($('.item.main')[0]);
  removeItem($('#item_'+s)[0]);
  ajaxPost({_touch:s}, function(data, dataType) {
    var v = $(data.main);
    if (isEdit) {
      v.find(".view").hide();
      v.find(".write").show();
    }
    prependItem($(data.sub)[0]);
    prependItem(v[0]);
  });
}
function mainEdit() {
  $(".view").toggle(200);
  $(".write").toggle(200, function() {
    masonry.layout();
  });
  return false;
}
function subEdit(s) {
  touchItem(s, true);
}
function mainWrite(s) {
  var t = $("#txt").val();
  removeItem($('.item.main')[0]);
  if (t == "") {
    removeItem($('.sub:first')[0]);
    ajaxPost({_delete:s}, function(data, dataType) {
      prependItem($(data.main)[0]);
    });
    return;
  }
  ajaxPost({_write:s, text:t}, function(data, dataType) {
    prependItem($(data.main)[0]);
  });
}
$(function(){
  $("#word").keypress(function(e) {
    if (e.which == 13) {
      touchItem(to64($("#word").val()));
      $("#word").val("");
    }
  });
  shortcut.add("e",function() {
    mainEdit();
  },{
    'disable_in_input':true
  });
  container = $(".masonry")[0];
  masonry = new Masonry(container, {
    itemSelector: '.item',
    columnWidth: 0,
    isFitWidth: true
  });
}); 

//-->
EOD
#================================================================
def files(f=false)
  $files = nil if f
  $files ||= Dir["d/*"].sort_by{|a|-File.stat(a).mtime.to_i}.
    map{|i| File.basename(i)}
end

def link_self(b, s)
  %|<a href="#" onclick="touchItem('#{b}')">#{s}</a>|
end
def link_word(s,c='nop')
  b = to64(s)
  return files[0] == b ? s : link_self(b, s)
end

def s2view(s)
  $words ||= files.map{|i| Regexp.escape(from64 i)}.join('|')
  esc(s).gsub(/((^,.+\n)+|\n)/){
    case $1
    when /((^,.+\n)+)/
      "<table>\n" + $1.split("\n").map{|i|
        "<tr>" + i.split(',').map{|i|
          i=='' ? '' : "<td>#{i}</td>"}.join + "</tr>\n"
      }.join + "</table>\n"
    when "\n" then "<br/>\n"
    end
  }.gsub(/( |\t|\[\[.+?\]\]|(http:|https:)\/\/[^\s<>]+|(#{$words}))/){
    case $1
    when " "
      then '&nbsp;'
    when "\t"
      then '&nbsp;&nbsp;&nbsp;&nbsp;'
    when %r!\[\[rest:(\d+)/(\d+)/(\d+)\]\]!
      then ((Time.local($1,$2,$3) - Time.now) / (60*60*24)).ceil
    when /\[\[((?:http:|https:)\S+?)\s+?(.+?)\]\]/
      then %|<a href="#{$1}" target="_blank">#{$2}</a>|
    when /\[\[(\S+?)\]\]/
      then %|<a href="?#{CGI.escape(unesc($1))}">#{$1}</a>|
    when /((http:|https:)\/\/[^\s<>]+)/
      then %|<a href="#{$1}" target="_blank">#{$1}</a>|
    when /(#{$words})/
      then link_word($1,'auto')
    else '?'
    end
  }
end

def xlink(t)
  w = from64(t)
  s = []
  files.map{|i| from64 i}.each do |i|
    s << link_word(i) + '<br/>' if i =~ /#{t}/ && i != t
  end
  s = ['<p>'] + s + ['</p>'] if 0 < s.size
  files.each do |i|
    next if i == t
    d = open('d/'+i){|f|f.read}
    n = d.scan(/^.*#{w}.*$/)
    next if n.size < 1
    s << "<p>#{esc('>>')} #{link_word(from64 i)}<br/>"+
      "#{s2view n.join("\n")}</p>"
  end
  return s.size < 1 ? '' : '<h2>Link</h2>' + s.join
end

def xmain(t)
  return <<EOD unless test('f', 'd/'+t)
<div id="item_#{t}" class="item main">
<h1>#{from64 t}</h1>
<div class="write">
  <textarea id="txt"></textarea>
  <input type="submit" id="write" value="Write" onClick="mainWrite('#{t}')"/>
</div>
</div>
EOD
  txt = open('d/'+t){|f|f.read}
  <<EOD
<div id="item_#{t}" class="item main">
<div style="float:right;">
  <a href="#" onclick="mainEdit()">[Edit]</a>
</div>
<h1>#{from64 t}</h1>

<div class="write" style="display: none">
<textarea id="txt">
#{txt}
</textarea>
<input type="submit" id="write" value="Write" onClick="mainWrite('#{t}')"/>\
<input type="submit" id="close" value="Close" onclick="mainEdit()"/>
</div>

<div class="view">
#{s2view txt}
#{xlink t}
</div>

</div>
EOD
end

def xsub(t)
  return '' unless t
  return '' unless test('f', 'd/'+t)
  a = open('d/'+t){|f|f.read}.split(/^----$/)
  <<EOD
<div id="item_#{t}" class="item sub">
<div style="float:right;">
  <a href="#" onclick="subEdit('#{t}')">[Edit]</a>
</div>
<h1>#{link_word(from64 t)}</h1>
#{s2view a[0]}
#{a.size < 2 ? '' : link_self(t, '&gt ReadMore...')}
</div>
EOD
end

def xall()
  return '' if files.size < 1
  a = [xmain(files[0])]
  (1 .. files.size-1).each{|i| a.push xsub(files[i])}
  a.join
end

#================================================================
def main
#----------------------------------------------------------------
  if cgip(:_touch)
    s = files[0]
    return '' if s == cgip(:_touch)
    n = 'd/'+cgip(:_touch)
    FileUtils.touch(n) if test('f', n)
    files(true)
    return contentJson(<<EOD)
{
  "main" : #{s2json xmain(cgip(:_touch))},
  "sub"  : #{s2json xsub(s)}
}
EOD
  end
#----------------------------------------------------------------
  if cgip(:_write)
    open('d/'+cgip(:_write),"w"){|f|f.write(cgip(:text).chomp)}
    return contentJson(<<EOD)
{
  "main" : #{s2json xmain(cgip(:_write))}
}
EOD
  end
#----------------------------------------------------------------
  if cgip(:_delete)
    s = 'd/'+cgip(:_delete)
    File.unlink(s) if test('f', s)
    s = files(true)[0]
    return contentJson(<<EOD)
{
  "main" : #{s2json xmain(s)},
  "sub"  : #{s2json s}
}
EOD
  end
#----------------------------------------------------------------
  return <<EOD
Content-type: text/html; charset=utf-8

<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta http-equiv="Content-Script-Type" content="text/javascript" />
  <meta http-equiv="Content-Style-Type" content="text/css" />
  <meta name="robots" content="noindex,nofollow">
  <meta name="robots" content="noarchive">
  <meta name="viewport" content="width=device-width">
  <title> #{SITE_NAME} </title>
  <link rel="shortcut icon" href="favicon.ico" /> 
  <script type="text/javascript" src="./jquery-2.1.3.min.js"></script>
  <script type="text/javascript" src="./shortcut.js"></script>
  <script type="text/javascript" src="./masonry.pkgd.min.js"></script>
  <script type="text/javascript" src="./base64.min.js"></script>
</head>
<style type="text/css">#{CSS}</style>
<script type="text/javascript">#{SCRIPT}</script>
<body>
<!-- ================================== -->
<div id="header">
Word <input id="word" type="text" size="12" name="word" value=""/>
<div style="float:right">
#{SITE_NAME}
</div>
</div>
<!-- ================================== -->
<div class="masonry">
<!-- ================================ -->
#{xall()}
<!-- ================================ -->
</div>
<!-- ================================== -->
</body>
</html>
EOD
end
#================================================================
puts main
