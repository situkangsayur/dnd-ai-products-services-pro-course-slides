def jalankan(tujuan, alat, model, maks_langkah=8):
    riwayat = [{"peran": "tujuan", "isi": tujuan}]
    for langkah in range(maks_langkah):
        pilihan = model.pilih(riwayat, daftar=alat.skema())
        if pilihan.selesai:
            return pilihan.jawaban, riwayat
        if pilihan.nama not in alat:
            riwayat.append({"peran": "galat", "isi": "alat tidak ada"})
            continue
        hasil = alat[pilihan.nama](**pilihan.argumen)
        riwayat.append({"peran": "amatan", "isi": hasil})
    return None, riwayat            # anggaran habis, bukan selesai
