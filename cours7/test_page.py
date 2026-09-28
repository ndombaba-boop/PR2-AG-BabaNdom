import html
commentaire = "x onmouseover=alert(1)"
c = html.escape(commentaire)
page = f"""
<div class={c}>         
 <p>{c}</p>
</div>""" 

print(page)