# Arguably a dumb structure but it works for now
class it:
    # Segna le variabili con {} e usa .format() per sostituirle
    source_code =  "https://github.com/NotLatif/CuloBot"
    issues =  "https://github.com/NotLatif/CuloBot/issues"
    nothing_changed =  "Non è cambiato niente."
    done =  "Fatto"

    class commands:
        join_message =  "A %name% piace il culo!"
        joinmsg_none =  "Il server non ha un messaggio di benvenuto, `!joinmsg help` per informazioni"
        joinmsg_info =  "`!joinmsg [msg]`: cambia il messaggio di benvenuto\nPuoi usare %name% nel messaggio per riferirti ad un utente eg: `!joinmsg A %name% piace il culo 🍑`\nUsa `!joinmsg false` per disattivarlo"
        joinmsg_deactivated =  "Hai disattivato la risposta"
        joinmsg_new_message =  "Il nuovo messaggio di benvenuto è: `{}`"
        
        leavemsg_none =  "Il server non ha un messaggio di addio, `!leavemsg help` per informazioni"
        leavemsg_info =  "`!leave [msg]`: cambia il messaggio di addio\nPuoi usare %name% nel messaggio per riferirti ad un utente eg: `!joinmsg A %name% piace il culo 🍑`\nUsa `!joinmsg false` per disattivarlo"
        leavemsg_deactivated =  "Hai disattivato la risposta"
        leavemsg_new_message =  "Il nuovo messaggio di addio è: `{}`"

        resp_info =  "Rispondo il {}% delle volte"
        resp_resp_to_bots_info =  "Risposta ai bot: {}\nRispondo il {}% delle volte"
        resp_resp_to_bots_affirmative =  "Okay, culificherò anche i bot 🍑"
        resp_resp_to_bots_negative =  "Niente culi per i bot 🤪"
        resp_resp_to_bots_invalid =  "Ehm, non ho capito? cosa vuoi fare con i bot?"
        resp_resp_to_bots_edit =  "ok, risponderò il {}% delle volte ai bot"
        resp_newperc =  "ok, risponderò il {}% delle volte"

        words_id_not_found =  "Id parola non trovato, `!words` per la lista di parole"
        words_learned =  "Nuova parola imparata!"
        words_info =  "Comandi disponibili:\n`/dictionary del <x>` per eliminare una parola\n`/dictionary edit <x> <parola>` per cambiare una parola\n`/dictionary add <parola>` per aggiungere una parola nuova\n`/dictionary del <id>` per rimuovere una parola nuova\n`/dictionary useDefault [true|false]` per scegliere se usare le parole globali\neg: `/dictionary add il culo, i culi` < per un esperienza migliore specifica l'articolo e la forma singolare(plurale)\neg: `/dictionary add culo` < specificare le forme non è obbligatorio\n**Puoi modificare solo le parole di {}.**"
        words_use_global_words =  "\n**{} non usa le parole globali, quindi non verranno mostrate**, per mostrarle usare il comando: `/dictionary useDefault `"
        words_known_words =  "Ecco le parole che conosco: "
        words_words =  "Prole del bot:"
        words_guild_words =  "Prole di {}:"
        words_no_guild_words =  "Nessuna parola impostata, usa `!words help` per più informazioni"

        help_description =  "I comandi vanno preceduti da '!', questo bot fa uso di ignoranza artificiale"
        help_footer =  "Ogni cosa è stata creata da @NotLatif, se riscontrare bug sapete a chi dare la colpa. https://notlatif.github.io/CuloBot/"
        help_advice =  ["CONSIGLIO" "Per una leggibilità migliore, puoi vedere i comandi al sito del bot https://notlatif.github.io/CuloBot/"],
        help_resp_info =  "Chiedi al bot la percentuale di culificazione"
        help_resp_set =  "Imposta la percentuale di culificazione a [x]%"
        help_resp_bots_info =  "controlla le percentuale di risposta verso gli altri bot"
        help_resp_bots_set =  "Imposta la percentuale di culificazione contro altri bot a [x]%"
        help_resp_bots_bool =  "abilita/disabilita le culificazioni di messaggi di altri bot"
        help_resp_use_default_words =  "Indica se il bot può usare le parole globali"
        help_words_words =  "Usalo per vedere le parole che il bot conosce"
        help_words_edit =  "Usalo modificare le parole del server"
        help_words_structure =  ["Struttura di word: " "Per un esperienza migliore è consigliato usare gli articoli e specificare prima la forma singolare e poi quella plurale divise da una virgola e.g. `il culo, i culi`\n`il culo` `culo` `culo, culi` sono comunque forme accettabili"],
        
        help_playlist_info =  "Vedi le playlist salvate"
        help_playlist_edit =  "Salva/Modifica una playlist"
        help_playlist_remove =  "Rimuovi una playlist"
        help_playlist_play =  "Fa partire una canzone, per usarlo devi essere in un canale vocale\n<song> può essere [link spotify | link youtube | nome di una playlist salvata | titolo di una canzone]"
        help_playlist_p =  "Lo stesso di !play"

        help_music_info =  "!music shuffle <true/false>\n!music precision <int>"
        help_player_info =  ["Comandi del player" "Sono i comandi che puoi usare quando il bot riproduce una canzone (N.B. non tutti i comandi usano '!')"],
        help_player_skip =  "salta [x] tracce (default = 1 traccia)"
        help_player_lyrics =  "Mostra il testo di una traccia"
        help_player_shuffle =  "Scambia in modo casuale la queue"
        help_player_pause =  "Mette in pausa la traccia corrente"
        help_player_resume =  "Fa ripartire la traccia"
        help_player_stop =  "Cancella la queue ed esce dal canale vocale"
        help_player_clear =  "Cancella la queue"
        help_player_loop =  "default=song; [song] mette in loop la traccia; [queue] rimette le tracce in queue quando finisce di riprodurle"
        help_player_restart =  "fa ricominciare la traccia corrente"
        help_player_queue =  "rimanda il messaggio con la queue"
        help_player_remove =  "rimuove la traccia in posizone x"
        help_player_mv =  "sposta la traccia dalla posizone x alla posizione y (x,y > 0)"
        help_player_play =  "Aggiunge una traccia in coda"
        help_player_p =  "Lo stesso di !play"
        help_player_playnext =  "Aggiunge una traccia in testa"
        help_player_pnext =  "Lo stesso di !playnext"

        help_chess_boards =  "vedi i FEN disponibili"
        help_chess_design =  "vedi i design delle scacchiere disponibili `!chess design` per più informazioni"
        help_chess_see =  "genera e invia un immagine del FEN"
        help_chess_add =  "aggiungi una scacchiera (FEN)"
        help_chess_remove =  "rimuove una scacchiera (FEN)"
        help_chess_rename =  "rinomina una scacchiera (FEN)"
        help_chess_edit =  "modifica una scacchiera (FEN)"

        help_misc_rawdump =  "manda un messaggio con tutti i dati salvati di questo server"
        help_misc_joinmsg =  "Mostra il messaggio di benvenuto del bot, usa `!joinmsg help` per più informazioni\n"
        help_misc_leavemsg =  "Mostra il messaggio di addio del bot, usa `!joinmsg help` per più informazioni\n"
        help_misc_joinimage =  "Specifica se il bot può inviare o meno un immagine casuale quando entra qualcuno nel server\n"
        
        help_issues =  "Problemi? lascia un feedback qui"

    class chess:
        layout_description =  "Scacchiere disponibili:"
        layout_global_layouts =  "Scacchiere globali:"
        layout_guild_layouts =  "Scacchiere di {}:"
        layout_render_error =  "Qualcosa è andato storto, probabilmente il FEN è errato"
        layout_render_invalid =  "Invalid board"
        layout_render_select =  "Seleziona il layout"
        layout_add_exists =  "La schacchiera esiste già, usa\n`/chess-layouts` per vedere le scacchiere\n`/chess-layout edit` per modificare una scacchiera"
        layout_add_done =  "Ho aggiunto {} {} !"
        layout_edit_select =  "Seleziona il layout da modificare"
        layout_edit_title =  "Modifica il layout {}"
        layout_edit_ok =  "Ho modificato il FEN {} -> {}"
        layout_delete_ok =  "Ho eliminato {}, {}"
        layout_delete_select =  "Scegli il layout da eliminare"
        layout_no_layouts =  "Non esiste nessun layout del server"
        
        design_generated =  "{} ha generato il design {}"
        design_404 =  "Design non trovato, usa `!chess design` per vedere i design disponibili"
        design_render_select =  "Seleziona il design"
        design_add_exists =  "Il design esiste già, per modificarlo usa /chess-designs edit"
        design_add_done =  "Design aggiunto: **{}**: {}"
        design_no_designs =  "Non esiste nessun design del server"
        design_edit_title =  "Modifica il design {}"
        design_edit_ok =  "Ho modificato il design {} -> {}"
        design_edit_select =  "Scegli il design da modificare"
        design_delete_select =  "Scegli il design da eliminare"
        design_delete_ok =  "Ho eliminato {}, {}"

    class music:
        playlist_edit_select =  "Scegli la playlist da modificare"
        playlist_edit_title =  "Cambia i link di {}"
        playlist_delete_ok =  "Ho eliminato {}, {}"
        playlist_delete_select =  "Scegli la playlist da eliminare"
        playlist_404 =  "Non esiste nessun design del server"



    #"no way i'm doing the rest of this, sorry": ""