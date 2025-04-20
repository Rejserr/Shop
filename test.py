#this is  a test file to show you example of how to see problem in my table below

#id	incoming_goods_id	delivery_note	sscc	document_msi	barcode	item_code	description	uom	quantity	received_qty	created_at	difference	status_text
#70	47	Tovarni_1	SSCC1	MSI1	4021163107579	V25261	Ventil kutni Schell, 1/2"x3/8", bez matice	kom	6.00	0.00	2024-11-21 20:01:32.007	-6.00	Nije zaprimljeno
#71	48	Tovarni_1	SSCC1	MSI1	NULL	G09898	H-ventil dvocijevni Herz, kutni, za pločasti/aluminijski radijator, s reduciranim nazuvicama, krom	kom	2.00	0.00	2024-11-21 20:01:32.007	-2.00	Nije zaprimljeno
#72	49	Tovarni_1	SSCC1	MSI1	NULL	G09898	H-ventil dvocijevni Herz, kutni, za pločasti/aluminijski radijator, s reduciranim nazuvicama, krom	kom	6.00	0.00	2024-11-21 20:01:32.007	-6.00	Nije zaprimljeno
#73	50	Tovarni_1	SSCC1	MSI1	NULL	G22307	Holender matica eurokonus Herz, 3/4", 16x2 mm	kom	9.00	0.00	2024-11-21 20:01:32.007	-9.00	Nije zaprimljeno
#74	51	Tovarni_1	SSCC1	MSI1	NULL	G22307	Holender matica eurokonus Herz, 3/4", 16x2 mm	kom	10.00	0.00	2024-11-21 20:01:32.007	-10.00	Nije zaprimljeno


    #item_code = G09898 has 2 rows with quantity 2.00 and 6.00, this one witch has 6.00 is not recognized
    #item_code = G22307 has 2 rows with quantity 9.00 and 10.00, this one witch has 10.00 is not recognized

    #this is a problem because i want if i recipte 5 items of G09898 it will befilled first row with 2.00 and then second row with 3.00.
    #and if i recipte 10 items of G22307 it will befilled first row with 9.00 and then second row with 1.00.
    #and on the first row i canot have status "višak" because status "Višak can be only on secund row".