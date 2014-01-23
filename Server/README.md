La funzione per trovare il cammino circolare è in findpath.py. C'è la guida nel file "Findpath guide.txt".
findpath_edges.py è una variante di findpath, che non necessita dei nodi, ma solo degli archi e della loro lista di adiacenza (c'è un commento su come formattare l'input a riga 39). In pratica si parte dall'arco iniziale, lo si attraversa e si cerca il percorso. Anche l'arco finale viene attraversato.
nenese.py trova, dato un punto su un piano cartesiano, il più vicino tra quelli memorizzati in un vettore.
AdjList.py dovrebbe creare le liste di adiacenza degli archi (dato un arco, sono memorizzati i suoi vicini), ma ho presupposto che gli archi si incontrassero solo nei loro punti terminali.
dijkstra.py trova il percorso minimo tra due nodi (l'input è da formattare similmente a come avviene con findpath). Questo programma l'ho scritto solo ieri e non l'ho provato con molti casi di input, ma mi sembrava funzionare.
