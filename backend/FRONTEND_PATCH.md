# Cambios en el frontend (index de Mocca)

## 1. Apuntar al backend nuevo (obligatorio)
```ts
const WEBHOOK_HORARIOS = "https://TU-API.onrender.com/webhook/mocca_beauty";
const WEBHOOK_CONFIRMAR = "https://TU-API.onrender.com/webhook/citamocca";
```

## 2. Correo opcional del cliente (para mandarle su confirmación + Google Calendar)

En `BookingPage`, junto a los otros estados:
```ts
const [email, setEmail] = useState("");
```

En el `body` de `confirmar()` agrega la línea `email`:
```ts
body: JSON.stringify({
  encabezado: isExpress ? "SERVICIO EXPRESS" : "SERVICIO ESTÁNDAR",
  isExpress,
  nombre,
  fechaNacimiento,
  telefono,
  email: email.trim(),          // ← nuevo
  servicios: payloadServicios,
  manicurista: effectiveManicurista,
  horario,
  fecha: isoDate(fecha),
}),
```

Pasa las props a `<Step1 ... email={email} setEmail={setEmail} />`, agrégalas al tipo de `Step1` y al destructuring, y pon este campo justo después del grid de fecha/teléfono:
```tsx
<Field label="Correo (opcional)" error={null}>
  <input
    type="email"
    inputMode="email"
    autoComplete="email"
    value={email}
    onChange={(e) => setEmail(e.target.value)}
    placeholder="tucorreo@gmail.com"
    className="m-input"
  />
</Field>
```
Si el correo es inválido el backend lo ignora, la cita se agenda igual. Y en `ConfirmationScreen` puedes agregar una línea:
"Te enviamos los detalles a tu correo." (solo si escribió uno).
