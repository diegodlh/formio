def gaps(lista):
  gap_start = None
  gap_end = None

  for i in range(1, max(lista)+1):
    if i in lista:
      if gap_start:
        if gap_end:
          print('Faltan: {} - {}'.format(gap_start, gap_end))
        else:
          print('Falta: {}'.format(gap_start))
        gap_start = gap_end = None
    else:
      if gap_start:
        gap_end = i
      else:
        gap_start = i
  print('Última encuesta: {}'.format(max(lista)))
