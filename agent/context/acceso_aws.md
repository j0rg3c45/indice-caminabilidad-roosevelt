# Acceso AWS — CaliTrack (Gobierno de Datos)

Configuración de acceso a AWS para el proyecto. Son datos de configuración (no secretos):
el acceso real se hace vía SSO con login por navegador, no hay claves versionadas.

## SSO

- Portal SSO: https://d-906780cf79.awsapps.com/start
- Región: `us-east-1`
- Usuario: `gobiernodedatos.jorgecas@gmail.com`

## Perfiles del CLI

| Perfil | Cuenta | Rol | Acceso |
|---|---|---|---|
| **calitrack** | 285757764705 | PS-CaliTrack | S3, Lambda, Athena, Glue, QuickSight ← **usar este** |
| default | 802479323033 | PS-aca-quick-kiro-access | solo S3 |

**Regla:** usar SIEMPRE `--profile calitrack` para el trabajo del proyecto (tiene acceso
completo). El perfil `default` solo tiene S3.

## Recursos conocidos

- Bucket S3: `aca-prod-calitrack-sismo-cali`

## Cómo ingresar (comandos)

```powershell
# 1. Renovar el token (abre navegador; expira periódicamente)
aws sso login --profile calitrack

# 2. Verificar acceso
aws sts get-caller-identity --profile calitrack

# 3. Usar SIEMPRE --profile calitrack en cada comando, por ejemplo:
aws s3 ls s3://aca-prod-calitrack-sismo-cali/ --profile calitrack
```

## Notas importantes

- El token SSO expira cada cierto tiempo. Si un comando falla con `Token has expired`, volver a
  ejecutar `aws sso login --profile calitrack`.
- Usar `--profile calitrack` en TODOS los comandos (el `default` solo tiene S3 y es de otra cuenta).
- En Windows/PowerShell, para listar objetos con nombres con tildes, forzar UTF-8:

  ```powershell
  $env:PYTHONUTF8="1"; [Console]::OutputEncoding=[System.Text.Encoding]::UTF8
  ```

- **Convención de nombres:** todo recurso nuevo con prefijo `aca-prod-calitrack-*` y tag
  `Proyecto: CaliTrack`.
- **Sin permiso IAM:** no se pueden crear ni editar roles o políticas; solo usar los roles ya
  habilitados.
- Servicios disponibles con el perfil `calitrack`: S3, Lambda, Athena, Glue, QuickSight.
- No guardar claves de acceso ni tokens en el repositorio; el acceso es siempre vía SSO.
